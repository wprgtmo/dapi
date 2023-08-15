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

from domino.models.resources.type_ext import ExtTypes
from domino.schemas.resources.type_ext import ExtTypeBase
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.utils import get_result_count
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_count = "Select count(*) FROM resources.ext_types "
    str_query = "Select id, ext_code, type_file FROM resources.ext_types "
    
    dict_query = {'ext_code': " WHERE ext_code ilike '%" + criteria_value + "%'",
                  'type_file': " WHERE type_file ilike '%" + criteria_value + "%'"}
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
        
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY ext_code "
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db) for item in lst_data]
            
    return result

def create_dict_row(item, page, db: Session):
    
    new_row = {'id': item['id'], 'ext_code' : item['ext_code'], 'type_file': item['type_file']}
    if page != 0:
        new_row['selected'] = False
    return new_row

def get_one(ext_type_id: str, db: Session):  
    return db.query(ExtTypes).filter(ExtTypes.id == ext_type_id).first()

def get_one_by_ext_type(ext_type: str, db: Session):  
    return db.query(ExtTypes).filter(ExtTypes.ext_code == ext_type).first()
      
def new(request, db: Session, ext_type: ExtTypeBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_ext_type = get_one_by_ext_type(ext_type.ext_code, db=db)
    if db_ext_type:
        raise HTTPException(status_code=404, detail=_(locale, "status.exist_name"))
        
    db_ext_type = ExtTypes(ext_code=ext_type.ext_code, type_file=ext_type.type_file, created_by=currentUser['username'])
    
    try:
        db.add(db_ext_type)
        db.commit()
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "status.error_new_status")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "status.already_exist")
        
        raise HTTPException(status_code=403, detail=msg)
 
