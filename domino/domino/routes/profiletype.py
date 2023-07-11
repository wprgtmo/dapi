# Routes status.py
from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.profiletype import ProfileTypeBase
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from domino.services.profiletype import get_all, new
from starlette import status
from domino.auth_bearer import JWTBearer
  
profiletype_route = APIRouter(
    tags=["ProfileType"],
    dependencies=[Depends(JWTBearer())]   
)

@profiletype_route.get("/profiletype", response_model=Dict, summary="Get list of Profile of System")
def get_profiletype(request: Request, username: str, db: Session = Depends(get_db)):
    return get_all(request=request, username=username, db=db)

@profiletype_route.post("/profiletype", response_model=ResultObject, summary="Create a new profile type.")
def create_profiletype(request:Request, profiletype: ProfileTypeBase, db: Session = Depends(get_db)):
    return new(request=request, profiletype=profiletype, db=db)
