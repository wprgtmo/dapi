from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.resources.result_object import ResultObject
from domino.schemas.events.invitations import InvitationAccepted

from domino.services.events.invitations import generate_all_user, update, get_all_invitations_by_user, get_all_invitations_by_tourney
  
invitation_route = APIRouter(
    tags=["Invitations"],
    dependencies=[Depends(JWTBearer())]   
)

@invitation_route.get("/invitation", response_model=ResultObject, summary="Get All Invitations for user logued.")
def get_all(request:Request, profile_id: str, status_name:str, db: Session = Depends(get_db)):
    return get_all_invitations_by_user(request=request, profile_id=profile_id, status_name=status_name, db=db)

@invitation_route.get("/invitation/tourney/", response_model=ResultObject, summary="Get All Invitations for tourney.")
def get_for_tourney(request:Request, tourney_id: str, status_name:str='', db: Session = Depends(get_db)):
    return get_all_invitations_by_tourney(request=request, tourney_id=tourney_id, status_name=status_name, db=db)

@invitation_route.post("/invitation", response_model=ResultObject, summary="Generate user invitations")
def generate(request:Request, tourney_id: str, db: Session = Depends(get_db)):
    return generate_all_user(request=request, tourney_id=tourney_id, db=db)

@invitation_route.put("/invitation/{id}", response_model=ResultObject, summary="Accept or Rejected Invitation")
def update_invitation(request:Request, id: str, invitation: InvitationAccepted, db: Session = Depends(get_db)):
    return update(request=request, db=db, invitation_id=str(id), invitation=invitation)
