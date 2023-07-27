import math

import datetime
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _

from domino.models.resources.package import Packages
from domino.schemas.resources.package import PackagesBase, PackagesSchema
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.utils import get_result_count
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_where = "WHERE is_active=True " 
    str_count = "Select count(*) FROM resources.packages "
    str_query = "Select id, name, price, number_individual_tourney, number_pairs_tourney, number_team_tourney " +\
        "FROM resources.packages "
    
    dict_query = {'name': " AND name ilike '%" + criteria_value + "%'",
                  'price': " AND price = " + criteria_value,
                  'number_individual_tourney': " AND number_individual_tourney = %" + criteria_value + "%",
                  'number_pairs_tourney': " AND number_pairs_tourney = %" + criteria_value + "%",
                  'number_team_tourney': " AND number_team_tourney = %" + criteria_value + "%",
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
    
    str_query += " ORDER BY price " 
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db) for item in lst_data]
    
    return result

def create_dict_row(item, page, db: Session):
    
    new_row = {'id': item['id'], 'name' : item['name'], 'price' : item['price'],
               'number_individual_tourney' : item['number_individual_tourney'],
               'number_pairs_tourney' : item['number_pairs_tourney'],
               'number_team_tourney' : item['number_team_tourney']}
    if page != 0:
        new_row['selected'] = False
    return new_row

def get_one(package_id: str, db: Session):  
    return db.query(Packages).filter(Packages.id == package_id).first()

def get_one_by_id(package_id: str, db: Session): 
    result = ResultObject()  
    result.data = db.query(Packages).filter(Packages.id == package_id).first()
    return result

def new(request, db: Session, package: PackagesBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_package = Packages(name=package.name, price=package.price, number_individual_tourney=package.number_individual_tourney, 
                          number_pairs_tourney=package.number_pairs_tourney, number_team_tourney=package.number_team_tourney,
                          created_by=currentUser['username'])
    
    try:
        db.add(db_package)
        db.commit()
        db.refresh(db_package)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "package.error_new_package")               
        raise HTTPException(status_code=403, detail=msg)
 
def delete(request: Request, package_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    try:
        db_package = db.query(Packages).filter(Packages.id == package_id).first()
        if db_package:
            db_package.is_active = False
            db_package.updated_by = currentUser['username']
            db_package.updated_date = datetime.today()
            db.commit()
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "package.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "package.imposible_delete"))
    
def update(request: Request, package_id: str, package: PackagesBase, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
       
    db_package = db.query(Packages).filter(Packages.id == package_id).first()
    
    if db_package:
    
        db_package.name = package.name
        db_package.price = package.price
        db_package.number_individual_tourney = package.number_individual_tourney
        db_package.number_pairs_tourney = package.number_pairs_tourney
        db_package.number_team_tourney = package.number_team_tourney
        
        db_package.updated_by = currentUser['username']
        db_package.updated_date = datetime.today()
            
        try:
            db.add(db_package)
            db.commit()
            db.refresh(db_package)
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail=_(locale, "package.already_exist"))
            
    else:
        raise HTTPException(status_code=404, detail=_(locale, "package.not_found"))
