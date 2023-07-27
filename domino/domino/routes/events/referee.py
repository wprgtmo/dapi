from fastapi import APIRouter, Depends, Request

from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.resources.result_object import ResultObject
from domino.services.events.referee import new, remove_referee, get_all_referees_by_tourney

  
referee_route = APIRouter(
    tags=["Referees"],
    dependencies=[Depends(JWTBearer())]   
)

@referee_route.get("/referee", response_model=ResultObject, summary="Get All Referee for tourney.")
def get_for_tourney(
    request: Request,
    tourney_id: str,
    is_active: bool = True,
    page: int = 1, 
    per_page: int = 6, 
    db: Session = Depends(get_db)
):
    return get_all_referees_by_tourney(request=request, page=page, per_page=per_page, tourney_id=tourney_id, is_active=is_active, db=db)

@referee_route.post("/referee", response_model=ResultObject, summary="Create new referee")
def new_referee(request:Request, invitation_id: str, db: Session = Depends(get_db)):
    return new(request=request, invitation_id=invitation_id, db=db)

@referee_route.delete("/referee/{id}", response_model=ResultObject, summary="Deactivate a Referee by its ID.")
def delete_referee(request:Request, id: str, db: Session = Depends(get_db)):
    return remove_referee(request=request, referee_id=str(id), db=db)
