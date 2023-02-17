import math

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.package import Packages
from domino.schemas.package import PackagesBase, PackagesSchema
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=page, per_page=per_page)  
        
    str_where = "WHERE is_active=True " 
    str_count = "Select count(*) FROM resources.packages "
    str_query = "Select id, name, type, players_number, price FROM resources.packages "
    
    dict_query = {'name': " AND name ilike '%" + criteria_value + "%'",
                  'type': " AND tipo ilike '%" + criteria_value + "%'",
                  'players_number': " AND players_number = " + criteria_value,
                  'price': " AND price = " + criteria_value,
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
    
    str_query += " ORDER BY price " 
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        new_row = {'id': item['id'], 'name' : item['name'], 'type' : item['type'], 
                   'players_number' : item['players_number'], 'price' : item['price']}
        
        if page != 0:
            new_row['selected'] = False
            
        result.data.append(new_row)
    
    return result

def get_one(package_id: str, db: Session):  
    return db.query(Packages).filter(Packages.id == package_id).first()

def get_one_by_id(package_id: str, db: Session): 
    result = ResultObject()  
    result.data = db.query(Packages).filter(Packages.id == package_id).first()
    return result

def new(request, db: Session, package: PackagesBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    # currentUser = get_current_user(request)
    
    db_package = Packages(name=package.name, type=package.type, 
                         players_number=package.players_number, price=package.price)
    
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
    # currentUser = get_current_user(request)
    
    try:
        db_package = db.query(Packages).filter(Packages.id == package_id).first()
        if db_package:
            db_package.is_active = False
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
        db_package.type = package.type
        db_package.players_number = package.players_number
        db_package.price = package.price
        
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
