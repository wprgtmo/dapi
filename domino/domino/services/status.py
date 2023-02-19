import math

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.status import StatusElement
from domino.schemas.status import StatusBase
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_count = "Select count(*) FROM resources.entities_status "
    str_query = "Select id, name, description FROM resources.entities_status "
    
    dict_query = {'name': " WHERE name ilike '%" + criteria_value + "%'",
                  'description': " WHERE description ilike '%" + criteria_value + "%'"}
    
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
        
    str_query += " ORDER BY name "
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        if page != 0:
            result.data.append({'id': item['id'], 'name' : item['name'], 'description': item['description'], 'selected': False})
        else:
            result.data.append({'id': item['id'], 'name' : item['name'], 'description': item['description']})
            
    return result

def get_one(status_id: str, db: Session):  
    return db.query(StatusElement).filter(StatusElement.id == status_id).first()

def get_one_by_name(name: str, db: Session):  
    return db.query(StatusElement).filter(StatusElement.name == name).first()
      
def new(request, db: Session, status: StatusBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_status = get_one_by_name(status.name, db=db)
    if db_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.exist_name"))
        
    db_status = StatusElement(name=status.name, description=status.description, created_by=currentUser['username'])
    
    try:
        db.add(db_status)
        db.commit()
        db.refresh(db_status)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "status.error_new_country")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "status.already_exist")
        
        raise HTTPException(status_code=403, detail=msg)
 
