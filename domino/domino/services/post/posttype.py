import math

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _

from domino.models.post.post import PostType
from domino.schemas.post.post import PostTypeBase
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.utils import get_result_count
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_count = "Select count(*) FROM post.post_type "
    str_query = "Select id, name, description FROM post.post_type "
    
    dict_query = {'name': " WHERE name ilike '%" + criteria_value + "%'",
                  'description': " WHERE description ilike '%" + criteria_value + "%'"}
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
        
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
        
    str_query += " ORDER BY name "
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db) for item in lst_data]
            
    return result

def create_dict_row(item, page, db: Session):
    
    new_row = {'id': item['id'], 'name' : item['name'], 'description': item['description']}
    if page != 0:
        new_row['selected'] = False
    return new_row

def get_one(posttype_id: str, db: Session):  
    return db.query(PostType).filter(PostType.id == posttype_id).first()

def get_one_by_name(name: str, db: Session):  
    return db.query(PostType).filter(PostType.name == name).first()
      
def new(request, db: Session, posttype: PostTypeBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_posttype = get_one_by_name(posttype.name, db=db)
    if db_posttype:
        raise HTTPException(status_code=404, detail=_(locale, "posttype.exist_name"))
        
    db_posttype = PostType(name=posttype.name, description=posttype.description, created_by=currentUser['username'])
    
    try:
        db.add(db_posttype)
        db.commit()
        db.refresh(db_posttype)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "posttype.error_new_post_type")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'name':
                msg = msg + _(locale, "posttype.already_exist")
        
        raise HTTPException(status_code=403, detail=msg)