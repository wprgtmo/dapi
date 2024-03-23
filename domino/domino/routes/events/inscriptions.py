from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.resources.result_object import ResultObject
from domino.schemas.events.inscriptions import InscriptionsBase, InscriptionsCreated

from domino.services.events.inscriptions import get_all
  
inscriptions_route = APIRouter(
    tags=["Inscriptions"],
    dependencies=[Depends(JWTBearer())]   
)

@inscriptions_route.get("/inscriptions/{tourney_id}", response_model=ResultObject, summary="Get All Inscriptions for tourney.")
def get_inscriptions(
    request: Request,
    tourney_id: str,
    page: int = 1, 
    per_page: int = 6, 
    search: str = "",
    db: Session = Depends(get_db)
):
    return get_all(
        request=request, tourney_id=tourney_id, page=page, per_page=per_page, criteria_value=search, db=db)
    
# @inscriptions_route.post("/inscriptions/", response_model=ResultObject, summary="Create new player of tourney")
# def new_inscriptions(request:Request, invitation_id: str, db: Session = Depends(get_db)):
#     return new(request=request, invitation_id=str(invitation_id), db=db)

# def create_event(request:Request, profile_id: str, event: EventBase = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
#     return new(request=request, profile_id=profile_id, event=event.dict(), db=db, file=image)