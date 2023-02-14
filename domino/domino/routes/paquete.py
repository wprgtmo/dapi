from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.paquete import PaqueteBase, PaqueteSchema
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.paquete import get_all, get_all_data, new, get_one, delete, update
from starlette import status
from domino.auth_bearer import JWTBearer
  
paquete_route = APIRouter(
    tags=["Paquetes"],
    # dependencies=[Depends(JWTBearer())]   
)

@paquete_route.get("/paquete", response_model=ResultObject, summary="Obtener lista de Paquetes")
def get_paquetes(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@paquete_route.get("/paquete/nomencladores", response_model=ResultObject, summary="Obtener lista de Paquetes")
def get_lst_paquetes(request: Request, db: Session = Depends(get_db)):
    return get_all_data(request=request, db=db)

@paquete_route.get("/paquete/{id}", response_model=ResultObject, summary="Obtener un Paquete por su ID")
def get_paquete_by_id(id: int, db: Session = Depends(get_db)):
    return get_one(paquete_id=id, db=db)

@paquete_route.post("/paquete", response_model=ResultObject, summary="Crear un Paquete ")
def create_paquete(request:Request, paquete: PaqueteBase, db: Session = Depends(get_db)):
    return new(request=request, paquete=paquete, db=db)

@paquete_route.delete("/paquete/{id}", response_model=ResultObject, summary="Desactivar un Paquete por su ID")
def delete_paquete(request:Request, id: int, db: Session = Depends(get_db)):
    is_delete = delete(request=request, paquete_id=str(id), db=db)
    if is_delete:
        raise HTTPException(status_code=200, detail="Paquete Eliminado")
    else:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")

@paquete_route.put("/paquete/{id}", response_model=ResultObject, summary="Actualizar un Paquete por su ID")
def update_paquete(request:Request, id: int, paquete: PaqueteBase, db: Session = Depends(get_db)):
    return update(request=request, db=db, paquete_id=str(id), paquete=paquete)
