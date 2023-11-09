from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.events.tourney import TourneyBase, TourneyCreated, SettingTourneyCreated
from domino.schemas.resources.result_object import ResultObject

from domino.services.events.domino_round import get_all, get_one_by_id
    
from domino.services.events.domino_scale import get_all_players_by_tables, get_all_players_by_tables_and_round, get_all_pairs
  
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
    return get_all(request=request, page=page, per_page=per_page, tourney_id=tourney_id, criteria_key=criteria_key, 
                   criteria_value=criteria_value, db=db)

@rounds_route.get("/rounds/rounds/one/", response_model=Dict, summary="Obtain a list of Tables of One Round.")
def get_one_round(
    round_id: str,
    db: Session = Depends(get_db)
):
    return get_one_by_id(round_id=round_id, db=db)

@rounds_route.get("/rounds/tables/", response_model=Dict, summary="Obtain a list of Tables at Rounds.")
def get_tables(
    request: Request,
    tourney_id: str,
    round_id: str = '',
    page: int = 1, 
    per_page: int = 6, 
    db: Session = Depends(get_db)
):
    return get_all_players_by_tables(request=request, tourney_id=tourney_id, round_id=round_id, page=page, per_page=per_page, db=db)

@rounds_route.get("/rounds/tables/one/", response_model=Dict, summary="Obtain a list of Tables of One Round.")
def get_tables_by_rounds(
    request: Request,
    round_id: str,
    page: int = 1, 
    per_page: int = 6, 
    db: Session = Depends(get_db)
):
    return get_all_players_by_tables_and_round(request=request, round_id=round_id, page=page, per_page=per_page, db=db)

@rounds_route.get("/rounds/pairs/", response_model=Dict, summary="Obtain a list of Pairs at Rounds.")
def get_pairs_by_rounds(
    request: Request,
    round_id: str,
    page: int = 1, 
    per_page: int = 6, 
    db: Session = Depends(get_db)
):
    return get_all_pairs(request=request, page=page, per_page=per_page, round_id=round_id, db=db)