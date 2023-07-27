# Routes status.py
from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.resources.status import StatusBase
from domino.schemas.resources.result_object import ResultObject
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.services.resources.status import get_all, new
  
status_route = APIRouter(
    tags=["Status"],
    dependencies=[Depends(JWTBearer())]   
)

@status_route.get("/status", response_model=Dict, summary="Get list of Entity Status")
def get_status(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@status_route.post("/status", response_model=ResultObject, summary="Create a new entity status.")
def create_status(request:Request, status: StatusBase, db: Session = Depends(get_db)):
    return new(request=request, status=status, db=db)
