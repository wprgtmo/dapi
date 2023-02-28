import math

from datetime import datetime
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.post import Post
from domino.schemas.post import PostBase, PostSchema
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.services.status import get_one_by_name, get_one as get_one_status
from domino.app import _
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_count = "Select count(*) FROM post.post "
    str_query = "Select id, title, summary, image, entity_type, entity_id, publication_date, expire_date, status_id " +\
        "FROM post.post "
    
    dict_query = {'title': " WHERE title ilike '%" + criteria_value + "%'",
                  'summary': " WHERE summary ilike '%" + criteria_value + "%'",
                  'entity_type': " WHERE entity_type ilike '%" + criteria_value + "%'",
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
    
    str_query += " ORDER BY publication_date " 
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        new_row = {'id': item['id'], 'title' : item['title'], 'summary' : item['summary'],
                   'image' : item['image'], 'entity_type' : item['entity_type'],
                   'entity_id' : item['entity_id'], 'publication_date' : item['publication_date'], 
                   'expire_date' : item['expire_date'], 'status_id' : item['status_id']}
        
        if page != 0:
            new_row['selected'] = False
            
        result.data.append(new_row)
    
    return result

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
    
    if (post.publication_date and post.expire_date) and (post.publication_date > post.expire_date):
        raise HTTPException(status_code=404, detail=_(locale, "post.dates_incorrect"))
      
    db_post = Post(title=post.title, summary=post.summary, entity_type=post.entity_type, 
                   entity_id=post.entity_id, image=post.image, publication_date=post.publication_date,
                   expire_date=post.expire_date, status_id=one_status.id,
                   created_by=currentUser['username'], updated_by=currentUser['username'])
    
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
            
        if db_post.image != post.image:    
            db_post.image = post.image
            
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
