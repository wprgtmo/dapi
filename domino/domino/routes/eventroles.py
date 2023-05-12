# Routes status.py
from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.status import StatusBase
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from domino.services.status import get_all, new
from starlette import status
from domino.auth_bearer import JWTBearer
  
eventroles_route = APIRouter(
    tags=["EventRoles"],
    dependencies=[Depends(JWTBearer())]   
)

@eventroles_route.get("/eventroles", response_model=Dict, summary="Get list of Roles of Event")
def get_eventroles(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@eventroles_route.post("/eventroles", response_model=ResultObject, summary="Create a new event rol.")
def create_eventroles(request:Request, status: StatusBase, db: Session = Depends(get_db)):
    return new(request=request, status=status, db=db)
