import math

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.userprofile import ProfileType
from domino.schemas.profiletype import ProfileTypeSchema, ProfileTypeBase
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _
from domino.services.utils import get_result_count
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_count = "Select count(*) FROM enterprise.profile_type "
    str_query = "Select id, name, description FROM enterprise.profile_type "
    
    dict_query = {'name': " WHERE name ilike '%" + criteria_value + "%'",
                  'description': " WHERE description ilike '%" + criteria_value + "%'"}
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
        
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY id "
    
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

def get_one(id: str, db: Session):  
    return db.query(ProfileType).filter(ProfileType.id == id).first()

def get_one_by_name(name: str, db: Session):  
    return db.query(ProfileType).filter(ProfileType.name == name).first()
      
def new(request, db: Session, profiletype: ProfileTypeBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_pro_type = get_one_by_name(profiletype.name, db=db)
    if db_pro_type:
        raise HTTPException(status_code=404, detail=_(locale, "profiletype.exist_name"))
        
    db_pro_type = ProfileType(name=profiletype.name, description=profiletype.description, created_by=currentUser['username'])
    
    try:
        db.add(db_pro_type)
        db.commit()
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "profiletype.error_new_status")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "profiletype.already_exist")
        
        raise HTTPException(status_code=403, detail=msg)