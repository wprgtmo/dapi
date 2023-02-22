
import math

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.city import City
from domino.schemas.city import CitySchema, CityCreate
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.app import _

from domino.services.country import get_one as country_get_one
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=page, per_page=per_page) 
        
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
    
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where 
    str_count += str_where 
    str_query += str_where
    
    if page != 0:
        result = ResultData(page=page, per_page=per_page)  
        
        result.total = db.execute(str_count).scalar()
        result.total_pages=result.total/result.per_page if (result.total % result.per_page == 0) else math.trunc(result.total / result.per_page) + 1
    else:
        result = ResultObject()
        
    str_query += " ORDER BY city.name "
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
         
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        new_row = {'id': item['id'], 'name' : item['name'], 'country_id': item['country_id'], 
                   'country_name': item['country_name'], 'selected': False}
        
        if page != 0:
            new_row['selected'] = False
            
        result.data.append(new_row)
    
    return result

def get_one(city_id: int, db: Session):  
    return db.query(City).filter(City.id == city_id).first()

def get_one_by_id(city_id: int, db: Session):  
    result = ResultObject() 
    result.data = db.query(City).filter(City.id == city_id).first()
    return result

def new(request, db: Session, city: CitySchema):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    # currentUser = get_current_user(request)
    
    one_country = country_get_one(city.country_id, db=db)
    if not one_country:
        raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
    
    db_city = City(name=city.name, country_id=one_country.id)
    
    try:
        db.add(db_city)
        db.commit()
        db.refresh(db_city)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "city.error_new_city")
        raise HTTPException(status_code=403, detail=msg)
    
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
