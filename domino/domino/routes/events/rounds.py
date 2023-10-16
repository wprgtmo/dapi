from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.events.tourney import TourneyBase, TourneyCreated, SettingTourneyCreated
from domino.schemas.resources.result_object import ResultObject

from domino.services.events.tourney import get_all, new, get_one_by_id, delete, update, get_all_by_event_id, \
    get_amount_tables, configure_one_tourney
from domino.services.events.domino_scale import get_all_players_by_tables
  
rounds_route = APIRouter(
    tags=["Rounds"],
    dependencies=[Depends(JWTBearer())]   
)

@rounds_route.get("/rounds/rounds/", response_model=Dict, summary="Obtain a list of Rounds.")
def get_rounds(
    request: Request,
    tourney_id: str,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@rounds_route.get("/rounds/tables/", response_model=Dict, summary="Obtain a list of Tables at Rounds.")
def get_tables(
    request: Request,
    tourney_id: str,
    round_id: str,
    page: int = 1, 
    per_page: int = 6, 
    db: Session = Depends(get_db)
):
    return get_all_players_by_tables(request=request, tourney_id=tourney_id, round_id=round_id, page=page, per_page=per_page, db=db)

@rounds_route.get("/rounds/players/", response_model=Dict, summary="Obtain a list of Players at Rounds.")
def get_players(
    request: Request,
    tourney_id: str,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)