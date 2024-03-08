
import math

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.app import _

from domino.models.resources.city import City

from domino.schemas.resources.city import CitySchema, CityCreate
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.utils import get_result_count
from domino.services.resources.country import get_one as country_get_one
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_where = "WHERE city.is_active=True " 
    str_count = "Select count(*) "
    str_query = "Select city.id, city.name, country_id, country.name as country_name "
    
    str_from = "FROM resources.city city INNER JOIN resources.country country ON country.id = city.country_id "
    
    str_count += str_from
    str_query += str_from
    
    dict_query = {'name': " AND city.name ilike '%" + criteria_value + "%'",
                  'country_id': " AND city.country_id = " + criteria_value,
                  'country_name': " AND country.name ilike '%" + criteria_value + "%'",
                  }
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where 
    str_count += str_where 
    str_query += str_where
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY city.name "
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
         
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db) for item in lst_data]
    
    return result

def create_dict_row(item, page, db: Session):
    
    new_row = {'id': item['id'], 'name' : item['name'], 'country_id': item['country_id'], 
               'country_name': item['country_name']}
    if page != 0:
        new_row['selected'] = False
    return new_row
    
def get_one(city_id: int, db: Session):  
    return db.query(City).filter(City.id == city_id).first()

def get_one_by_name(city_name: str, db: Session):  
    return db.query(City).filter(City.name == city_name).first()

def get_one_by_id(city_id: int, db: Session):  
    result = ResultObject() 
    result.data = db.query(City).filter(City.id == city_id).first()
    return result

def get_list_by_country_id(country_id: int, db: Session):  
    return db.query(City).filter(City.country_id == country_id).first()

def new(request, db: Session, city: CitySchema):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    # currentUser = get_current_user(request)
    
    one_country = country_get_one(city.country_id, db=db)
    if not one_country:
        raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
    
    db_city = insert_new_city(one_country.id, city.name, db=db)
    if not db_city:
        raise HTTPException(status_code=404, detail=_(locale, "city.error_create_city"))
        
    return result

def insert_new_city(contry_id: str, city_name, db: Session):
    
    db_city = City(name=city_name, country_id=contry_id)
    
    try:
        db.add(db_city)
        db.commit()
        return db_city
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return None
        
def delete(request: Request, city_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    # currentUser = get_current_user(request)
    
    try:
        db_city = db.query(City).filter(City.id == city_id).first()
        if db_city:
            db_city.is_active = False
            db.commit()
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "city.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "city.imposible_delete"))
    
def update(request: Request, city_id: str, city: CityCreate, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    # currentUser = get_current_user(request) 
    
    one_country = country_get_one(city.country_id, db=db)
    if not one_country:
        raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
       
    db_city = db.query(City).filter(City.id == city_id).first()
    
    if db_city:
        db_city.name = city.name
        db_city.country_id = city.country_id
            
        try:
            db.add(db_city)
            db.commit()
            db.refresh(db_city)
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail=_(locale, "city.already_exist"))
    else:
        raise HTTPException(status_code=404, detail=_(locale, "city.not_found"))
