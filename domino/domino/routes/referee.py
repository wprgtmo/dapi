from fastapi import APIRouter, Depends, Request
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.referee import new, remove_referee
from starlette import status
from domino.auth_bearer import JWTBearer
  
referee_route = APIRouter(
    tags=["Referees"],
    dependencies=[Depends(JWTBearer())]   
)

@referee_route.get("/referee", response_model=ResultObject, summary="Get All Referee for tourney.")
def get_for_tourney(request:Request, tourney_id: str, status_name:str='', db: Session = Depends(get_db)):
    return new(request=request, tourney_id=tourney_id, status_name=status_name, db=db)

@referee_route.post("/referee", response_model=ResultObject, summary="Create new referee")
def new_player(request:Request, invitation_id: str, db: Session = Depends(get_db)):
    return new(request=request, invitation_id=invitation_id, db=db)

@referee_route.delete("/referee/{id}", response_model=ResultObject, summary="Deactivate a Referee by its ID.")
def delete_referee(request:Request, id: str, db: Session = Depends(get_db)):
    return remove_referee(request=request, referee_id=str(id), db=db)