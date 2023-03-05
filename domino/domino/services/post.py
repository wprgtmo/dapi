import math
import time

from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.post import Post, PostLikes, PostComments, PostShares, PostSharesUsers, PostImages
from domino.schemas.post import PostBase
from domino.schemas.postelement import PostImageCreate, PostLikeCreate, PostCommentCreate, PostShareCreate
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.services.status import get_one_by_name, get_one as get_one_status
from domino.services.posttype import get_one_by_name as get_posttype_by_name
from domino.app import _
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_count = "Select count(*) FROM post.post po LEFT JOIN enterprise.users us ON po.created_by = us.username "
    str_query = "Select po.id, title, summary, post_type, entity_id, publication_date, expire_date, status_id, " +\
        "us.first_name || ' ' || us.last_name as full_name, po.created_date, us.photo " +\
        "FROM post.post po LEFT JOIN enterprise.users us ON po.created_by = us.username "

    dict_query = {'title': " WHERE title ilike '%" + criteria_value + "%'",
                  'summary': " WHERE summary ilike '%" + criteria_value + "%'",
                  'post_type': " WHERE post_type ilike '%" + criteria_value + "%'",
                  'publication_date': " WHERE publication_date >= '%" + criteria_value + "%'",
                  }
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    if page != 0:
        result = ResultData(page=page, per_page=per_page)  
        
        result.total = db.execute(str_count).scalar()
        result.total_pages=result.total/result.per_page if (result.total % result.per_page == 0) else math.trunc(result.total / result.per_page) + 1
    else:
        result = ResultObject()
    
    str_query += " ORDER BY created_date DESC " 
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = []
    current_date = datetime.now()
    for item in lst_data:
        new_row = create_dict_row(item, current_date, db=db)
        if page != 0:
            new_row['selected'] = False
            
        result.data.append(new_row)
    
    return result

def create_dict_row(item, current_date, db: Session):
    
    amount_like, amount_comments, amount_shares = get_amount_element_of_post(item['id'], db=db)
    return {'id': item['id'], 'name' : item['title'] if item['title'] else "", 
            'avatar': item['photo'] if item['photo'] else "", 'summary': item['summary'] if item['summary'] else "",
            'elapsed': calculate_time(current_date, item['created_date']), 
            'amount_like': amount_like, 'amount_comments': amount_comments, 'amount_shares': amount_shares,
            'comments': get_comments_of_post(item['id'], current_date, db=db),
            'photos': get_images_of_post(item['id'], db=db)
            }

def calculate_time(current_date, star_date):
    
    diferencia = current_date - star_date
    days = diferencia.days
    
    if diferencia.days > 0:
        return str(days) + ' d'
    else:
        hours = diferencia.seconds // 3600
        if hours > 0:
            return str(hours) + ' h'
        else:
            minutes = diferencia.seconds // 60
            if minutes > 0:
                return str(minutes) + ' m'
            else:
                return str(diferencia.seconds) + ' s'
 
def get_amount_element_of_post(post_id, db: Session):
    
    str_count = "SELECT count(*) FROM "
    str_where = "where post_id = '" + post_id + "' "
    
    str_likes = str_count + "post.post_likes " + str_where 
    str_comments = str_count + "post.post_comments " + str_where 
    str_shares = str_count + "post.post_shares " + str_where
    
    amount_like = db.execute(str_likes).scalar()
    amount_comments = db.execute(str_comments).scalar()
    amount_shares = db.execute(str_shares).scalar()
   
    return amount_like, amount_comments, amount_shares

def get_comments_of_post(post_id: str, current_date: datetime, db: Session):
    
    str_comments = "SELECT po.id, us.first_name || ' ' || us.last_name as full_name, us.photo, summary, " +\
        "po.created_date FROM post.post_comments po " +\
        "LEFT JOIN enterprise.users us ON po.created_by = us.username " +\
        "WHERE post_id = '" + post_id + "' ORDER BY created_date LIMIT 3"
    lst_comments = db.execute(str_comments)
 
    lst_result = []
    for item_comment in lst_comments:
        lst_result.append({'id': item_comment['id'], 'name': item_comment['full_name'], 
                           'avatar': item_comment['photo'] if item_comment['photo'] else "", 
                           'comment': item_comment['summary'] if item_comment['summary'] else "", 
                           'elapsed': calculate_time(current_date, item_comment['created_date'])})
    
    return lst_result

def get_images_of_post(post_id: str, db: Session):
    
    str_images = "SELECT image FROM post.post_images WHERE post_id = '" + post_id + "' ORDER BY created_date "
    lst_images = db.execute(str_images)
 
    lst_result = []
    for item_image in lst_images:
        lst_result.append({'path': item_image['image']})
    
    return lst_result

def get_one(post_id: str, db: Session):  
    return db.query(Post).filter(Post.id == post_id).first()

def get_one_by_id(post_id: str, db: Session): 
    result = ResultObject()  
    result.data = db.query(Post).filter(Post.id == post_id).first()
    return result

def new(request, db: Session, post: PostBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_status = get_one_by_name('CREATED', db=db)
    if not one_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    if not post.entity_id:  # no esta sobre ninguna entidad
        posttype = get_posttype_by_name('APP', db=db)
    else:
        posttype = get_posttype_by_name(post.post_type, db=db)
    if not posttype:
        raise HTTPException(status_code=404, detail=_(locale, "posttype.not_found"))
    
    if (post.publication_date and post.expire_date) and (post.publication_date > post.expire_date):
        raise HTTPException(status_code=404, detail=_(locale, "post.dates_incorrect"))
      
    db_post = Post(title=post.title, summary=post.summary, post_type=posttype.name, 
                   entity_id=post.entity_id, publication_date=post.publication_date,
                   expire_date=post.expire_date, status_id=one_status.id,
                   created_by=currentUser['username'], updated_by=currentUser['username'])
    
    if post.images:
        for item_image in post.images:
            post_image = PostImages(image=item_image.image, created_by=currentUser['username'])
            db_post.images.append(post_image)
            # post_image = PostImages(post_id=db_post.id, image=item.image, created_by=currentUser['username'])
            
    try:
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_post")               
        raise HTTPException(status_code=403, detail=msg)

def delete(request: Request, post_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_status = get_one_by_name('CANCELLED', db=db)
    if not one_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    try:
        db_post = db.query(Post).filter(Post.id == post_id).first()
        if db_post:
            db_post.status_id = one_status.id
            db_post.updated_by = currentUser['username']
            db_post.updated_date = datetime.now()
            db.commit()
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "post.imposible_delete"))
    
def update(request: Request, post_id: str, post: PostBase, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
       
    db_post = db.query(Post).filter(Post.id == post_id).first()
    
    if db_post:
    
        one_status = get_one_status(post.status_id, db=db)
        if not one_status:
            raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
        if db_post.title != post.title:
            db_post.title = post.title
        
        if db_post.summary != post.summary:    
            db_post.summary = post.summary
            
        if db_post.publication_date != post.publication_date:    
            db_post.publication_date = post.publication_date
            
        if db_post.expire_date != post.expire_date:    
            db_post.expire_date = post.expire_date
            
        if db_post.status_id != post.status_id:    
            db_post.status_id = one_status.status.id
        
        db_post.updated_by = currentUser['username']
        db_post.updated_date = datetime.now()
                
        try:
            db.add(db_post)
            db.commit()
            db.refresh(db_post)
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail=_(locale, "post.already_exist"))
            
    else:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))

def add_one_image(request, db: Session, postimage: PostImageCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_post = get_one(postimage.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    db_postimage = PostImages(post_id=postimage.post_id, image=postimage.image, created_by=currentUser['username'])
    
    try:
        db.add(db_postimage)
        db.commit()
        db.refresh(db_postimage)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_postimage")               
        raise HTTPException(status_code=403, detail=msg)
    
def remove_one_image(request: Request, db: Session, postimage_id: str):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_post_image = db.query(PostImages).filter(PostImages.id == postimage_id).first()
    if not db_post_image:
        raise HTTPException(status_code=404, detail=_(locale, "post.image_not_found"))
    
    try:
        db.delete(db_post_image)
        db.commit()
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_remove_postimage")               
        raise HTTPException(status_code=403, detail=msg)
    
def add_one_likes(request, db: Session, postlike: PostLikeCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_post = get_one(postlike.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    db_postlike = PostLikes(post_id=postlike.post_id, created_by=currentUser['username'])
    
    try:
        db.add(db_postlike)
        db.commit()
        db.refresh(db_postlike)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_postlike")               
        raise HTTPException(status_code=403, detail=msg)
    
def add_one_comment(request, db: Session, postcomment: PostCommentCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_post = get_one(postcomment.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    db_postcomment = PostComments(post_id=postcomment.post_id, summary=postcomment.summary, created_by=currentUser['username'])
    
    try:
        db.add(db_postcomment)
        db.commit()
        db.refresh(db_postcomment)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_postcomment")               
        raise HTTPException(status_code=403, detail=msg)
    
def add_one_share(request, db: Session, postshare: PostShareCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_post = get_one(postshare.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    db_postshare = PostShares(post_id=postshare.post_id, summary=postshare.summary, created_by=currentUser['username'])
    
    try:
        db.add(db_postshare)
        db.commit()
        db.refresh(db_postshare)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_postshare")               
        raise HTTPException(status_code=403, detail=msg)