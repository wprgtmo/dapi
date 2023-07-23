# Routes request.py
from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.request import RequestAccepted
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from domino.services.request import get_request_to_confirm_at_profile, update
from starlette import status
from domino.auth_bearer import JWTBearer
  
request_route = APIRouter(
    tags=["RequestPlayer"],
    dependencies=[Depends(JWTBearer())]   
)

@request_route.get("/requestplayer/one/{profile_id}", response_model=ResultObject, summary="Get Request to confirm")
def get_request_to_confirm(request:Request, profile_id: str, db: Session = Depends(get_db)):
    return get_request_to_confirm_at_profile(request=request, profile_id=profile_id, db=db)

@request_route.put("/requestplayer/{profile_id}", response_model=ResultObject, summary="Acept or Refuse Request to play")
def update_request(request:Request, profile_id:str, requestprofile: RequestAccepted,  db: Session = Depends(get_db)):
    return update(request=request, db=db, profile_id=profile_id, requestprofile=requestprofile)