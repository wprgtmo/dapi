from fastapi import APIRouter, Depends, Request
from starlette import status
from domino.auth_bearer import JWTBearer
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict

from domino.schemas.resources.result_object import ResultObject
from domino.services.events.player import new, remove_player, get_all_players_by_tourney, reject_one_invitation

  
player_route = APIRouter(
    tags=["Players"],
    dependencies=[Depends(JWTBearer())]   
)

@player_route.get("/player", response_model=Dict, summary="Get All Players for tourney.")
def get_for_tourney(
    request: Request,
    tourney_id: str,
    is_active: bool = True,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all_players_by_tourney(request=request, page=page, per_page=per_page, tourney_id=tourney_id, is_active=is_active, 
                                      criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@player_route.post("/player/confirmed/{invitation_id}", response_model=ResultObject, summary="Create new player")
def confirm_player(request:Request, invitation_id: str, db: Session = Depends(get_db)):
    return new(request=request, invitation_id=str(invitation_id), db=db)

@player_route.post("/player/rejected/{invitation_id}", response_model=ResultObject, summary="Reject invitation to player")
def reject_player(request:Request, invitation_id: str, db: Session = Depends(get_db)):
    return reject_one_invitation(request=request, invitation_id=str(invitation_id), db=db)

@player_route.delete("/player/{id}", response_model=ResultObject, summary="Deactivate a Player by its ID.")
def delete_player(request:Request, id: str, db: Session = Depends(get_db)):
    return remove_player(request=request, player_id=str(id), db=db)
