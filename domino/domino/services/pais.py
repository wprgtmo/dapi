import math

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.pais import Pais
from domino.schemas.pais import PaisBase, PaisSchema
from domino.schemas.result_object import ResultObject
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
    str_count = "Select count(*) FROM configuracion.pais "
    str_query = "Select id, nombre FROM configuracion.pais "
    
    dict_query = {'nombre': " AND nombre ilike '%" + criteria_value + "%'",
                  'is_active': " AND is_active = " + criteria_value + ""
                  }
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
        
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where 
    str_count += str_where 
    str_query += str_where
    
    result.total = db.execute(str_count).scalar()
    result.total_pages=result.total/result.per_page if (result.total % result.per_page == 0) else math.trunc(result.total / result.per_page) + 1
    
    str_query += " ORDER BY nombre LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        result.data.append({'id': item['id'], 'nombre' : item['nombre'], 'selected': False})
    
    return result

def get_all_data(request:Request, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=0, per_page=0, total=0, total_pages=0) 
        
    str_query = "Select id, nombre FROM configuracion.pais WHERE is_active=True "
    
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        result.data.append({'id': item['id'], 'nombre' : item['nombre']})
    
    return result
 
def get_one(pais_id: str, db: Session):  
    return db.query(Pais).filter(Pais.id == pais_id).first()

def get_one_by_name(nombre: str, db: Session):  
    return db.query(Pais).filter(Pais.nombre == nombre, Pais.is_active == True).first()
      
def get_one_by_id(pais_id: str, db: Session): 
    result = ResultObject(page=0, per_page=0, total=0, total_pages=0) 
    result.data = db.query(Pais).filter(Pais.id == pais_id).first()
    return result
 
def new(request, db: Session, pais: PaisBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=0, per_page=0, total=0, total_pages=0) 
    # currentUser = get_current_user(request)
    
    db_pais = get_one_by_name(pais.nombre)
    if db_pais:
        raise HTTPException(status_code=404, detail=_(locale, "pais.exist_name"))
        
    db_pais = Pais(nombre=pais.nombre)
    
    try:
        db.add(db_pais)
        db.commit()
        db.refresh(db_pais)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "pais.error_nuevo_pais")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "pais.already_exist")
        
        raise HTTPException(status_code=403, detail=msg)
 
def delete(request: Request, pais_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=0, per_page=0, total=0, total_pages=0) 
    # currentUser = get_current_user(request)
    
    try:
        db_pais = db.query(Pais).filter(Pais.id == pais_id).first()
        if db_pais:
            db_pais.is_active = False
            db.commit()
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "pais.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "pais.imposible_delete"))
    
def update(request: Request, pais_id: str, pais: PaisBase, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=0, per_page=0, total=0, total_pages=0) 
    currentUser = get_current_user(request) 
    
    db_pais = get_one_by_name(pais.nombre)
    if db_pais:
        raise HTTPException(status_code=404, detail=_(locale, "pais.exist_name"))
       
    db_pais = db.query(Pais).filter(Pais.id == pais_id).first()
    
    if db_pais:
    
        db_pais.nombre = pais.nombre
        
        try:
            db.add(db_pais)
            db.commit()
            db.refresh(db_pais)
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail=_(locale, "pais.already_exist"))
            
    else:
        raise HTTPException(status_code=404, detail=_(locale, "pais.not_found"))
