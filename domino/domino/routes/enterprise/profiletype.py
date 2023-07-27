# Routes status.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.enterprise.profiletype import ProfileTypeBase
from domino.schemas.resources.result_object import ResultObject

from domino.services.enterprise.profiletype import get_all, new
  
profiletype_route = APIRouter(
    tags=["Nomenclators"],  # tags=["ProfileType"],
    dependencies=[Depends(JWTBearer())]   
)

@profiletype_route.get("/profiletype", response_model=Dict, summary="Get list of Profile of System")
def get_profiletype(request: Request, db: Session = Depends(get_db)):
    return get_all(request=request, db=db)

@profiletype_route.post("/profiletype", response_model=ResultObject, summary="Create a new profile type.")
def create_profiletype(request:Request, profiletype: ProfileTypeBase, db: Session = Depends(get_db)):
    return new(request=request, profiletype=profiletype, db=db)
