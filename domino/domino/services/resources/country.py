import math

from fastapi import HTTPException, Request
from unicodedata import name
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _

from domino.models.resources.country import Country
from domino.schemas.resources.country import CountryBase
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.utils import get_result_count
            
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
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
        
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where 
    str_count += str_where 
    str_query += str_where
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
        
    str_query += " ORDER BY name "
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db) for item in lst_data]
    
    return result

def create_dict_row(item, page, db: Session):
    
    new_row = {'id': item['id'], 'name' : item['name']}
    if page != 0:
        new_row['selected'] = False
    return new_row

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
        
    db_country = insert_new_country(country.name, db=db)
    if not db_country:
        raise HTTPException(status_code=404, detail=_(locale, "country.error_create_country"))
        
    return result
        
def insert_new_country(contry_name: str, db: Session):
    
    db_country = Country(name=contry_name)
    
    try:
        db.add(db_country)
        db.commit()
        return db_country
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return None
    
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
