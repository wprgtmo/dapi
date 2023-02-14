import math

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.paquetes import Paquete
from domino.schemas.paquete import PaqueteBase, PaqueteSchema
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject(page=page, per_page=per_page)  
        
    str_where = "WHERE is_active=True " 
    str_count = "Select count(*) FROM configuracion.paquetes "
    str_query = "Select id, nombre, tipo, cantidad_jugadores, precio FROM configuracion.paquetes "
    
    dict_query = {'nombre': " AND nombre ilike '%" + criteria_value + "%'",
                  'tipo': " AND tipo ilike '%" + criteria_value + "%'",
                  'is_active': " AND is_active = " + criteria_value + ""
                  }
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail="Parametro no válido")
    
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where 
    str_count += str_where 
    str_query += str_where
    
    result.total = db.execute(str_count).scalar()
    result.total_pages=result.total/result.per_page if (result.total % result.per_page == 0) else math.trunc(result.total / result.per_page) + 1
    
    str_query += " ORDER BY precio LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        result.data.append({'id': item['id'], 'nombre' : item['nombre'], 'tipo' : item['tipo'], 
                            'cantidad_jugadores' : item['cantidad_jugadores'], 
                            'precio' : item['precio'], 'selected': False})
    
    return result
 
def get_one(paquete_id: str, db: Session):  
    return db.query(Paquete).filter(Paquete.id == paquete_id).first()

def get_all_data(request:Request, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()  
        
    str_query = "Select id, nombre, tipo, cantidad_jugadores, precio FROM configuracion.paquetes WHERE is_active=True ORDER BY precio "
    
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        result.data.append({'id': item['id'], 'nombre' : item['nombre'], 'tipo' : item['tipo'], 
                            'cantidad_jugadores' : item['cantidad_jugadores'], 
                            'precio' : item['precio'], 'selected': False})
    
    return result
       
def new(request, db: Session, paquete: PaqueteBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    # currentUser = get_current_user(request)
    
    db_paquete = Paquete(nombre=paquete.nombre, tipo=paquete.tipo, cantidad_jugadores=paquete.cantidad_jugadores, precio=paquete.precio)
    
    try:
        db.add(db_paquete)
        db.commit()
        db.refresh(db_paquete)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = 'Ha ocurrido un error al crear el pais'               
        raise HTTPException(status_code=403, detail=msg)
 
def delete(request: Request, paquete_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()
    # currentUser = get_current_user(request)
    
    try:
        db_paquete = db.query(Paquete).filter(Paquete.id == paquete_id).first()
        if db_paquete:
            db_paquete.is_active = False
            db.commit()
            return result
        else:
            raise HTTPException(status_code=404, detail="No encontrado")
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail="No es posible eliminar")
    
def update(request: Request, paquete_id: str, paquete: PaqueteBase, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()
    currentUser = get_current_user(request) 
       
    db_paquete = db.query(Paquete).filter(Paquete.id == paquete_id).first()
    
    if db_paquete:
    
        db_paquete.nombre = paquete.nombre
        db_paquete.tipo = paquete.tipo
        db_paquete.cantidad_jugadores = paquete.cantidad_jugadores
        db_paquete.precio = paquete.precio
        
        try:
            db.add(db_paquete)
            db.commit()
            db.refresh(db_paquete)
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail="Ya existe un paquete con esos datos")
            
    else:
        raise HTTPException(status_code=400, detail="No existe un paquete con este ID")
