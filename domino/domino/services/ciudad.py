
import math
from unicodedata import name
from fastapi import HTTPException
from domino.models.ciudad import Ciudad
from domino.schemas.ciudad import CiudadBase, CiudadSchema, CiudadInfo
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from typing import Dict, List

from domino.services.pais import get_one as pais_get_one
            
def get_all(request: List[CiudadInfo], skip: int, limit: int, db: Session):  
    data = db.query(Ciudad).offset(skip).limit(limit).all()   
    lst_data = []
    for item in data: 
        lst_data.append(create_row_ciudad(item))
    return lst_data

def get_all(page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
        
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
        raise HTTPException(status_code=404, detail="Parametro no válido")
    
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where 
    str_count += str_where 
    str_query += str_where
    
    total = db.execute(str_count).scalar()
    total_pages=total/per_page if (total % per_page == 0) else math.trunc(total / per_page) + 1
    
    str_query += " ORDER BY ciudad.nombre LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    data = []
    for item in lst_data:
        data.append({'id': item['id'], 'nombre' : item['nombre'], 
                     'pais_id': item['pais_id'], 'pais_nombre': item['pais_nombre'],
                     'selected': False})
    
    return {"page": page, "per_page": per_page, "total": total, "total_pages": total_pages, "data": data}

def create_row_ciudad(item):
    
    one_ciudad = CiudadInfo()
    one_ciudad.id = item.id
    one_ciudad.nombre = item.nombre
    one_ciudad.pais_id = item.pais_id
    one_ciudad.pais = item.pais.nombre
    return one_ciudad
        
def new(request, db: Session, ciudad: CiudadSchema):
    
    # currentUser = get_current_user(request)
    
    one_pais = pais_get_one(ciudad.pais_id, db=db)
    if not one_pais:
        raise HTTPException(status_code=404, detail='Pais no Existe')
    
    db_ciudad = Ciudad(nombre=ciudad.nombre, pais_id=one_pais.id)
    
    try:
        db.add(db_ciudad)
        db.commit()
        db.refresh(db_ciudad)
        return True
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = 'Ha ocurrido un error al crear la ciudad'               
        raise HTTPException(status_code=403, detail=msg)
    
def get_one(ciudad_id: str, db: Session):  
    return db.query(Ciudad).filter(Ciudad.id == ciudad_id).first()

def delete(ciudad_id: str, db: Session):
    try:
        db_ciudad = db.query(Ciudad).filter(Ciudad.id == ciudad_id).first()
        db.delete(db_ciudad)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail="No es posible eliminar")
    
def update(ciudad_id: str, ciudad: CiudadSchema, db: Session):
       
    db_ciudad = db.query(Ciudad).filter(Ciudad.id == ciudad_id).first()
    
    if db_ciudad:
        db_ciudad.nombre = ciudad.nombre
        db_ciudad.pais_id = ciudad.pais_id
            
        try:
            db.add(db_ciudad)
            db.commit()
            db.refresh(db_ciudad)
            return db_ciudad
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail="Ya existe una ciudad con este Nombre")
    else:
        raise HTTPException(status_code=400, detail="No existe ciudad con ese ID")
