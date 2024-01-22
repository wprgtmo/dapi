from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.resources.status import StatusBase
from domino.schemas.resources.result_object import ResultObject
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.resources.playercategories import EventLevelsBase, EventScopesBase, PlayerCategoriesBase

from domino.services.resources.playercategories import get_all_event_level, get_all_event_scope, new_event_level, new_event_scope, new_category_by_elo
  
eventscategories_route = APIRouter(
    tags=["Nomenclators"],
    dependencies=[Depends(JWTBearer())]   
)

@eventscategories_route.get("/eventlevels/", response_model=Dict, summary="Get list of levels of Events")
def get_events_levels(
    request: Request,
    db: Session = Depends(get_db)
):
    return get_all_event_level(request=request, db=db)

@eventscategories_route.get("/eventscopes/", response_model=Dict, summary="Get list of Scopes of Events")
def get_events_scopes(
    request: Request,
    db: Session = Depends(get_db)
):
    return get_all_event_scope(request=request, db=db)

@eventscategories_route.post("/eventlevels/", response_model=ResultObject, summary="Create a new entity events levels.")
def create_events_levels(request:Request, eventslevels: EventLevelsBase, db: Session = Depends(get_db)):
    return new_event_level(request=request, eventslevels=eventslevels, db=db)

@eventscategories_route.post("/eventscopes/", response_model=ResultObject, summary="Create a new entity events scopes.")
def create_events_scopes(request:Request, eventscopes: EventScopesBase, db: Session = Depends(get_db)):
    return new_event_scope(request=request, eventscopes=eventscopes, db=db)

@eventscategories_route.post("/playercategory/", response_model=ResultObject, summary="Create a new entity of category player.")
def create_player_category(request:Request, playercategory: PlayerCategoriesBase, db: Session = Depends(get_db)):
    return new_category_by_elo(request=request, playercategory=playercategory, db=db)
