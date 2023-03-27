import math
import time

from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.post import Post, PostLikes, PostComments, PostFiles, CommentComments, CommentLikes
from domino.schemas.post import PostBase, PostUpdated
from domino.schemas.postelement import PostFileCreate, PostLikeCreate, PostCommentCreate, CommentCommentCreate, CommentLikeCreate
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _
from domino.services.utils import get_result_count
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_count = "Select count(*) FROM post.post po LEFT JOIN enterprise.users us ON po.created_by = us.username "
    str_query = "Select po.id, summary, us.first_name || ' ' || us.last_name as full_name, po.created_date, us.photo " +\
        "FROM post.post po LEFT JOIN enterprise.users us ON po.created_by = us.username "

    dict_query = {'summary': " WHERE summary ilike '%" + criteria_value + "%'",
                  'created_by': " WHERE created_by = '" + criteria_value + "'"
                  }
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    str_query += " ORDER BY created_date DESC " 
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    current_date = datetime.now()
    result.data = [create_dict_row(item, current_date, db=db) for item in lst_data]
    
    return result

def get_list_post(request:Request, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    current_date = datetime.now()
    date_find = datetime.now() - timedelta(days=4)
    currentUser = get_current_user(request)
    
    str_query = "Select po.id, summary, us.first_name || ' ' || us.last_name as full_name, po.created_date, us.photo " +\
        "FROM post.post po JOIN enterprise.users us ON po.created_by = us.username " +\
        "LEFT JOIN enterprise.user_followers usf ON usf.user_follow = po.created_by " +\
        "WHERE po.is_active=True AND po.updated_date >= '" + date_find.strftime('%Y-%m-%d') + "' " +\
        "AND (usf.username = '" + currentUser['username'] + "' or po.created_by = 'domino' or po.created_by = '" + currentUser['username'] + "')"
    
    str_query += " ORDER BY created_date DESC " 
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, current_date, currentUser, db=db) for item in lst_data]
    
    return result

def create_dict_row(item, current_date, currentUser, db: Session):
    
    amount_like, amount_comments = get_amount_element_of_post(item['id'], db=db)
    return {'id': item['id'], 
            'name': item['full_name'],
            'avatar': item['photo'] if item['photo'] else "", 
            'elapsed': calculate_time(current_date, item['created_date']), 
            'comment': item['summary'] if item['summary'] else "",
            'amountLike': amount_like, 'amountComment': amount_comments, 
            'comments': get_comments_of_post(item['id'], current_date, db=db),
            'photos': get_files_of_post(item['id'], db=db),
            'like': verify_likes(str(item['id']), currentUser['username'], db=db)
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

def verify_likes(post_id, username, db: Session):
    
    str_count = "SELECT count(id) FROM post.post_likes Where post_id = '" +\
        post_id + "' and created_by = '" + username + "'"
    
    exist_like = db.execute(str_count).scalar()    
    return True if exist_like else False
 
def get_amount_element_of_post(post_id, db: Session):
    
    str_count = "SELECT count(*) FROM "
    str_where = "where post_id = '" + post_id + "' "
    
    str_likes = str_count + "post.post_likes " + str_where 
    str_comments = str_count + "post.post_comments " + str_where 
    
    amount_like = db.execute(str_likes).scalar()
    amount_comments = db.execute(str_comments).scalar()
    
    return amount_like, amount_comments

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

def get_files_of_post(post_id: str, db: Session):
    
    str_files = "SELECT path FROM post.post_files WHERE post_id = '" + post_id + "' "
    lst_files = db.execute(str_files)
 
    lst_result = []
    for item_file in lst_files:
        lst_result.append({'path': item_file['path']})
    
    return lst_result

def get_one(post_id: str, db: Session):  
    return db.query(Post).filter(Post.id == post_id).first()

def get_one_postcomment(comment_id: str, db: Session):  
    return db.query(PostComments).filter(PostComments.id == comment_id).first()

def get_one_by_id(post_id: str, db: Session): 
    result = ResultObject()  
    result.data = db.query(Post).filter(Post.id == post_id).first()
    return result

def new(request, db: Session, post: PostBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_post = Post(summary=post.summary, created_by=currentUser['username'], updated_by=currentUser['username'],
                   is_active=True)
    
    if post.files:
        for item_file in post.files:
            post_file = PostFiles(path=item_file)
            db_post.files.append(post_file)
            
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
    
    try:
        db_post = db.query(Post).filter(Post.id == post_id).first()
        if db_post:
            db_post.is_active = False
            db_post.updated_by = currentUser['username']
            db_post.updated_date = datetime.now()
            db.commit()
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "post.imposible_delete"))
    
def update(request: Request, post_id: str, post: PostUpdated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
       
    db_post = db.query(Post).filter(Post.id == post_id).first()
    
    if db_post:
    
        if db_post.summary != post.summary:    
            db_post.summary = post.summary
        
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

def add_one_file(request, db: Session, postfile: PostFileCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_post = get_one(postfile.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    db_postfile = PostFiles(post_id=postfile.post_id, path=postfile.path, created_by=currentUser['username'])
    
    try:
        db.add(db_postfile)
        db.commit()
        db.refresh(db_postfile)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_postimage")               
        raise HTTPException(status_code=403, detail=msg)
    
def remove_one_file(request: Request, db: Session, postfile_id: str):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_post_file = db.query(PostFiles).filter(PostFiles.id == postfile_id).first()
    if not db_post_file:
        raise HTTPException(status_code=404, detail=_(locale, "post.file_not_found"))
    
    try:
        db.delete(db_post_file)
        db.commit()
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_remove_postfile")               
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
    
def add_one_likes_at_comment(request, db: Session, commentlike: CommentLikeCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_comment = get_one_postcomment(commentlike.comment_id, db=db)
    if not one_comment:
        raise HTTPException(status_code=404, detail=_(locale, "post.comment_not_found"))
    
    db_commentlike = CommentLikes(comment_id=commentlike.comment_id, created_by=currentUser['username'])
    
    try:
        db.add(db_commentlike)
        db.commit()
        db.refresh(db_commentlike)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_commentlike")               
        raise HTTPException(status_code=403, detail=msg)
    
def add_one_comment_at_comment(request, db: Session, commentcomment: CommentCommentCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_post = get_one_postcomment(commentcomment.comment_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.comment_not_found"))
    
    db_comment_comment = CommentComments(post_id=commentcomment.post_id, summary=commentcomment.summary, created_by=currentUser['username'])
    
    try:
        db.add(db_comment_comment)
        db.commit()
        db.refresh(db_comment_comment)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_commentcomment")               
        raise HTTPException(status_code=403, detail=msg)
    
