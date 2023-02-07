# Routes pais.py
from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.pais import PaisBase, PaisSchema
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.pais import get_all, new, get_one, delete, update
from starlette import status
from domino.auth_bearer import JWTBearer
import uuid
  
pais_route = APIRouter(
    tags=["Paises"],
    # dependencies=[Depends(JWTBearer())]   
)

@pais_route.get("/pais", response_model=Dict, summary="Obtener lista de Paises")
def get_paises(
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@pais_route.post("/pais", summary="Crear un País")
def create_pais(request:Request, pais: PaisBase, db: Session = Depends(get_db)):
    return new(request=request, pais=pais, db=db)

@pais_route.get("/pais/{id}", response_model=PaisSchema, summary="Obtener un Pais por su ID")
def get_pais_by_id(id: int, db: Session = Depends(get_db)):
    return get_one(pais_id=id, db=db)

@pais_route.delete("/pais/{id}", status_code=status.HTTP_200_OK, summary="Eliminar un Pais por su ID")
def delete_pais(id: int, db: Session = Depends(get_db)):
    is_delete = delete(pais_id=str(id), db=db)
    if is_delete:
        raise HTTPException(status_code=200, detail="Pais Eliminado")
    else:
        raise HTTPException(status_code=404, detail="Pais no encontrado")

@pais_route.put("/pais/{id}", summary="Actualizar un Pais por su ID")
def update_pais(id: int, pais: PaisBase, db: Session = Depends(get_db)):
    return update(db=db, pais_id=str(id), pais=pais)
