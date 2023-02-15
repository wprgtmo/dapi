# Routes pais.py
from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.pais import PaisBase, PaisSchema
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.pais import get_all, get_all_data, new, get_one_by_id, delete, update
from starlette import status
from domino.auth_bearer import JWTBearer
import uuid
  
pais_route = APIRouter(
    tags=["Paises"],
    dependencies=[Depends(JWTBearer())]   
)

@pais_route.get("/pais", response_model=ResultObject, summary="Obtener lista de Paises con paginado")
def get_paises(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@pais_route.get("/pais/nomencladores", response_model=ResultObject, summary="Obtener listado de Paises sin paginado")
def get_lst_data(request: Request, db: Session = Depends(get_db)):
    return get_all_data(request=request, db=db)

@pais_route.get("/pais/{id}", response_model=ResultObject, summary="Obtener un Pais por su ID")
def get_pais_by_id(id: int, db: Session = Depends(get_db)):
    return get_one_by_id(pais_id=id, db=db)

@pais_route.post("/pais", response_model=ResultObject, summary="Crear un País")
def create_pais(request:Request, pais: PaisBase, db: Session = Depends(get_db)):
    return new(request=request, pais=pais, db=db)

@pais_route.delete("/pais/{id}", response_model=ResultObject, summary="Eliminar un Pais por su ID")
def delete_pais(request:Request, id: int, db: Session = Depends(get_db)):
    return delete(request=request, pais_id=str(id), db=db)
    
@pais_route.put("/pais/{id}", response_model=ResultObject, summary="Actualizar un Pais por su ID")
def update_pais(request:Request, id: int, pais: PaisBase, db: Session = Depends(get_db)):
    return update(request=request, db=db, pais_id=str(id), pais=pais)
