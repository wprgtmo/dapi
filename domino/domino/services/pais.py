import math

from unicodedata import name
from fastapi import HTTPException
from domino.models.pais import Pais
from domino.schemas.pais import PaisBase, PaisSchema
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from typing import List
            
def get_all(page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
        
    str_where = "WHERE is_active=True " 
    str_count = "Select count(*) FROM configuracion.pais "
    str_query = "Select id, nombre FROM configuracion.pais "
    
    dict_query = {'nombre': " AND nombre ilike '%" + criteria_value + "%'",
                  'is_active': " AND is_active = " + criteria_value + ""
                  }
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail="Parametro no válido")
    
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where 
    str_count += str_where 
    str_query += str_where
    
    total = db.execute(str_count).scalar()
    total_pages=total/per_page if (total % per_page == 0) else math.trunc(total / per_page) + 1
    
    str_query += " ORDER BY nombre LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    data = []
    for item in lst_data:
        data.append({'id': item['id'], 'nombre' : item['nombre'], 'selected': False})
    
    return {"page": page, "per_page": per_page, "total": total, "total_pages": total_pages, "data": data}
        
def new(request, db: Session, pais: PaisBase):
    
    # currentUser = get_current_user(request)
    
    db_pais = Pais(nombre=pais.nombre)
    
    try:
        db.add(db_pais)
        db.commit()
        db.refresh(db_pais)
        return True
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = 'Ha ocurrido un error al crear el pais'               
        raise HTTPException(status_code=403, detail=msg)
    
def get_one(pais_id: str, db: Session):  
    return db.query(Pais).filter(Pais.id == pais_id).first()

def delete(pais_id: str, db: Session):
    try:
        db_pais = db.query(Pais).filter(Pais.id == pais_id).first()
        if db_pais:
            db_pais.is_active = False
            # db.delete(db_pais)
            db.commit()
            return True
        else:
            raise HTTPException(status_code=404, detail="No encontrado")
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail="No es posible eliminar")
    
def update(pais_id: str, pais: PaisBase, db: Session):
       
    db_pais = db.query(Pais).filter(Pais.id == pais_id).first()
    
    if db_pais:
    
        db_pais.nombre = pais.nombre
        
        try:
            db.add(db_pais)
            db.commit()
            db.refresh(db_pais)
            return True
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail="Ya existe un pais con este Nombre")
            
    else:
        raise HTTPException(status_code=400, detail="No existe un pais con este ID")
