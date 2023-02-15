
import math

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.ciudad import Ciudad
from domino.schemas.ciudad import CiudadBase, CiudadSchema, CiudadInfo
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from typing import Dict, List
from domino.app import _

from domino.services.pais import get_one as pais_get_one
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=page, per_page=per_page) 
        
    str_where = "WHERE ciudad.is_active=True " 
    str_count = "Select count(*) "
    str_query = "Select ciudad.id, ciudad.nombre, pais_id, pais.nombre as pais_nombre "
    
    str_from = "FROM configuracion.ciudad ciudad INNER JOIN configuracion.pais pais ON pais.id = ciudad.pais_id "
    
    str_count += str_from
    str_query += str_from
    
    dict_query = {'nombre': " AND ciudad.nombre ilike '%" + criteria_value + "%'",
                  'pais_nombre': " AND pais.nombre ilike '%" + criteria_value + "%'",
                  }
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where 
    str_count += str_where 
    str_query += str_where
    
    result.total = db.execute(str_count).scalar()
    result.total_pages=result.total/result.per_page if (result.total % result.per_page == 0) else math.trunc(result.total / result.per_page) + 1
    
    str_query += " ORDER BY ciudad.nombre LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        result.data.append(
            {'id': item['id'], 'nombre' : item['nombre'], 'pais_id': item['pais_id'], 
             'pais_nombre': item['pais_nombre'], 'selected': False})
    
    return result

def get_all_data(request:Request, db: Session, pais_id: int):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=0, per_page=0, total=0, total_pages=0) 
        
    str_query = "Select ciudad.id, ciudad.nombre, pais_id, pais.nombre as pais_nombre " \
        "FROM configuracion.ciudad ciudad INNER JOIN configuracion.pais pais ON " \
        "pais.id = ciudad.pais_id WHERE ciudad.is_active=True " 
        
    if pais_id:
        str_query += " AND pais_id = " + str(pais_id)
    
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        result.data.append( {'id': item['id'], 'nombre' : item['nombre']})
    
    return result

def get_one(ciudad_id: int, db: Session):  
    return db.query(Ciudad).filter(Ciudad.id == ciudad_id).first()

def get_one_by_id(ciudad_id: int, db: Session):  
    result = ResultObject(page=0, per_page=0, total=0, total_pages=0) 
    result.data = db.query(Ciudad).filter(Ciudad.id == ciudad_id).first()
    return result

def new(request, db: Session, ciudad: CiudadSchema):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=0, per_page=0, total=0, total_pages=0) 
    # currentUser = get_current_user(request)
    
    one_pais = pais_get_one(ciudad.pais_id, db=db)
    if not one_pais:
        raise HTTPException(status_code=404, detail=_(locale, "pais.not_found"))
    
    db_ciudad = Ciudad(nombre=ciudad.nombre, pais_id=one_pais.id)
    
    try:
        db.add(db_ciudad)
        db.commit()
        db.refresh(db_ciudad)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "ciudad.error_nueva_ciudad")
        raise HTTPException(status_code=403, detail=msg)
    
def delete(request: Request, ciudad_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=0, per_page=0, total=0, total_pages=0) 
    # currentUser = get_current_user(request)
    
    try:
        db_ciudad = db.query(Ciudad).filter(Ciudad.id == ciudad_id).first()
        if db_ciudad:
            db_ciudad.is_active = False
            db.commit()
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "ciudad.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "ciudad.imposible_delete"))
    
def update(request: Request, ciudad_id: str, ciudad: CiudadSchema, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=0, per_page=0, total=0, total_pages=0) 
    # currentUser = get_current_user(request) 
    
    one_pais = pais_get_one(ciudad.pais_id, db=db)
    if not one_pais:
        raise HTTPException(status_code=404, detail=_(locale, "pais.not_found"))
       
    db_ciudad = db.query(Ciudad).filter(Ciudad.id == ciudad_id).first()
    
    if db_ciudad:
        db_ciudad.nombre = ciudad.nombre
        db_ciudad.pais_id = ciudad.pais_id
            
        try:
            db.add(db_ciudad)
            db.commit()
            db.refresh(db_ciudad)
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail=_(locale, "ciudad.already_exist"))
    else:
        raise HTTPException(status_code=404, detail=_(locale, "ciudad.not_found"))
