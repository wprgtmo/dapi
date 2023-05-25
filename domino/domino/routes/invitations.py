from fastapi import APIRouter, Depends, Request
from domino.schemas.result_object import ResultObject
from domino.schemas.invitations import InvitationAccepted
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.invitations import generate_all_user, get_all_sent_by_user, update, get_all_accept_by_user, get_all_invitations_by_user
from starlette import status
from domino.auth_bearer import JWTBearer
  
invitation_route = APIRouter(
    tags=["Invitations"],
    dependencies=[Depends(JWTBearer())]   
)

@invitation_route.get("/invitation/confirm/", response_model=ResultObject, summary="Get Invites to confirm.")
def get_invitations_to_confirm(request:Request, db: Session = Depends(get_db)):
    return get_all_sent_by_user(request=request, db=db)

@invitation_route.get("/invitation/accept/", response_model=ResultObject, summary="Get accepted Invitates ")
def get_invitations_accepted(request:Request, db: Session = Depends(get_db)):
    return get_all_accept_by_user(request=request, db=db)

@invitation_route.get("/invitation/all/", response_model=ResultObject, summary="Get All Invitations for user logued.")
def get_all_invitations(request:Request, db: Session = Depends(get_db)):
    return get_all_invitations_by_user(request=request, db=db)

@invitation_route.post("/invitation", response_model=ResultObject, summary="Generate user invitations")
def generate(request:Request, tourney_id: str, db: Session = Depends(get_db)):
    return generate_all_user(request=request, tourney_id=tourney_id, db=db)

@invitation_route.put("/invitation/{id}", response_model=ResultObject, summary="Accept or Rejected Invitation")
def update_invitation(request:Request, id: str, invitation: InvitationAccepted, db: Session = Depends(get_db)):
    return update(request=request, db=db, invitation_id=str(id), invitation=invitation)
