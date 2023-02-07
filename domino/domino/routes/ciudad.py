# Routes ciudad.py
from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.ciudad import CiudadBase, CiudadSchema, CiudadCreate
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.ciudad import get_all, new, get_one, delete, update
from starlette import status
from domino.auth_bearer import JWTBearer
import uuid
  
ciudad_route = APIRouter(
    tags=["Ciudades"],
    # dependencies=[Depends(JWTBearer())]   
)

@ciudad_route.get("/ciudad", response_model=Dict, summary="Obtener lista de Ciudades")
def get_ciudades(
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@ciudad_route.post("/ciudad", summary="Crear una Ciudad")
def create_ciudad(request:Request, ciudad: CiudadCreate, db: Session = Depends(get_db)):
    return new(request, ciudad=ciudad, db=db)

@ciudad_route.get("/ciudad/{id}", response_model=CiudadSchema, summary="Obtener una ciudad por su ID")
def get_ciudad_by_id(id: int, db: Session = Depends(get_db)):
    return get_one(ciudad_id=id, db=db)

@ciudad_route.delete("/ciudad/{id}", status_code=status.HTTP_200_OK, summary="Eliminar una Ciudad por su ID")
def delete_ciudad(id: int, db: Session = Depends(get_db)):
    is_delete = delete(ciudad_id=str(id), db=db)
    if is_delete:
        raise HTTPException(status_code=200, detail="Ciudad Eliminada")
    else:
        raise HTTPException(status_code=404, detail="Ciudad no encontrado")

@ciudad_route.put("/ciudad/{id}", response_model=CiudadSchema, summary="Actualizar una Ciudad por su ID")
def update_ciudad(id: int, ciudad: CiudadSchema, db: Session = Depends(get_db)):
    return update(db=db, ciudad_id=str(id), ciudad=ciudad)
