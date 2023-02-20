import math

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.country import Country
from domino.schemas.country import CountryBase
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_where = "WHERE is_active=True " 
    str_count = "Select count(*) FROM resources.country "
    str_query = "Select id, name FROM resources.country "
    
    dict_query = {'name': " AND name ilike '%" + criteria_value + "%'",
                  'is_active': " AND is_active = " + criteria_value + ""
                  }
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
        
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where 
    str_count += str_where 
    str_query += str_where
    
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
            result.data.append({'id': item['id'], 'name' : item['name'], 'selected': False})
        else:
            result.data.append({'id': item['id'], 'name' : item['name']})
            
    return result

def get_one(country_id: str, db: Session):  
    return db.query(Country).filter(Country.id == country_id).first()

def get_one_by_name(name: str, db: Session):  
    return db.query(Country).filter(Country.name == name, Country.is_active == True).first()
      
def get_one_by_id(request, country_id: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 
    result.data = db.query(Country).filter(Country.id == country_id).first()
    if not result.data:
        raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
    
    return result
 
def new(request, db: Session, country: CountryBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    # currentUser = get_current_user(request)
    
    db_country = get_one_by_name(country.name, db=db)
    if db_country:
        raise HTTPException(status_code=404, detail=_(locale, "country.exist_name"))
        
    db_country = Country(name=country.name)
    
    try:
        db.add(db_country)
        db.commit()
        db.refresh(db_country)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "country.error_new_country")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "country.already_exist")
        
        raise HTTPException(status_code=403, detail=msg)
 
def delete(request: Request, country_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    # currentUser = get_current_user(request)
    
    try:
        db_country = db.query(Country).filter(Country.id == country_id).first()
        if db_country:
            db_country.is_active = False
            db.commit()
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "country.imposible_delete"))
    
def update(request: Request, country_id: str, country: CountryBase, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    db_country = get_one_by_name(country.name, db=db)
    if db_country:
        raise HTTPException(status_code=404, detail=_(locale, "country.exist_name"))
       
    db_country = db.query(Country).filter(Country.id == country_id).first()
    
    if db_country:
    
        db_country.name = country.name
        
        try:
            db.add(db_country)
            db.commit()
            db.refresh(db_country)
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail=_(locale, "country.already_exist"))
            
    else:
        raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))