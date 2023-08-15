# Routes status.py
from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.resources.type_ext import ExtTypeBase
from domino.schemas.resources.result_object import ResultObject
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.services.resources.type_ext import get_all, new
  
type_ext_route = APIRouter(
    tags=["Nomenclators"],
    dependencies=[Depends(JWTBearer())]   
)

@type_ext_route.get("/ext_type", response_model=Dict, summary="Get list of Ext Types")
def get_ext_type(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@type_ext_route.post("/ext_type", response_model=ResultObject, summary="Create a new entity ext_type.")
def create_ext_type(request:Request, ext_type: ExtTypeBase, db: Session = Depends(get_db)):
    return new(request=request, ext_type=ext_type, db=db)
