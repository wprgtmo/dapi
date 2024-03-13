from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.events.tourney import TourneyCreated
from domino.schemas.resources.result_object import ResultObject

from domino.services.events.domino_table import get_all as get_all_tables_for_tourney
from domino.services.events.tourney import get_all, new, get_one_by_id, delete, update, \
    get_amount_tables, update_image_tourney, close_one_tourney
    
from domino.services.events.player import created_all_players
  
tourney_route = APIRouter(
    tags=["Tourney"],
    dependencies=[Depends(JWTBearer())]   
)

# solo los creados por ese perfil
@tourney_route.get("/tourney/{profile_id}", response_model=Dict, summary="Obtain a list of Tourney.")
def get_tourney(
    request: Request,
    profile_id: str, 
    page: int = 1, 
    per_page: int = 6, 
    search: str = "", 
    db: Session = Depends(get_db)
):
    return get_all(request=request, profile_id=profile_id, page=page, per_page=per_page, criteria_value=search, db=db)

@tourney_route.get("/tourney/tables/{id}", response_model=Dict, summary="Get List of Tables for Tourney.")
def get_all_tables(
    request:Request,
    id: str, 
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)):
    return get_all_tables_for_tourney(
        request=request, tourney_id=id, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

# @tourney_route.get("/tourney/event/{event_id}", response_model=ResultObject, summary="Get List of Tourney for Event.")
# def get_by_event(event_id: str, db: Session = Depends(get_db)):
#     return get_all_by_event_id(event_id=event_id, db=db)

@tourney_route.get("/tourney/one/{id}", response_model=ResultObject, summary="Get a Tourney for your ID.")
def get_tourney_by_id(id: str, db: Session = Depends(get_db)):
    return get_one_by_id(tourney_id=id, db=db)

@tourney_route.post("/tourney/{profile_id}", response_model=ResultObject, summary="Create a Tourney..")
def create_tourney(request:Request, profile_id: str, tourney: TourneyCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return new(request=request, profile_id=profile_id, tourney=tourney.dict(), image=image, db=db)

# @tourney_route.put("/tourney/image/{id}", response_model=ResultObject, summary="Update Image of Tourney.")
# def update_image(request:Request, id: str, image: UploadFile = "", db: Session = Depends(get_db)):
#     return update_image_tourney(request=request, tourney_id=str(id), db=db, file=image)

@tourney_route.delete("/tourney/{id}", response_model=ResultObject, summary="Deactivate a Tourney by its ID.")
def delete_tourney(request:Request, id: str, db: Session = Depends(get_db)):
    return delete(request=request, tourney_id=str(id), db=db)
    
@tourney_route.put("/tourney/{id}", response_model=ResultObject, summary="Update a Tourney by its ID")
def update_tourney(request:Request, id: str, tourney: TourneyCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return update(request=request, db=db, tourney_id=id, tourney=tourney.dict(), image=image)

@tourney_route.post("/tourney/close/{id}", response_model=ResultObject, summary="Close a Tourney by its ID")
def close_tourney(request:Request, id: str, db: Session = Depends(get_db)):
    return close_one_tourney(request=request, db=db, tourney_id=id)

@tourney_route.post("/tourney/setting/tables/{id}", response_model=ResultObject, summary="Get amount tables")
def amount_tables(request:Request, id: str, db: Session = Depends(get_db)):
    return get_amount_tables(request=request, tourney_id=id, db=db)

@tourney_route.post("/tourney/player/confirmed/{id}", response_model=ResultObject, summary="Confirm all players")
def confirm_player_to_tourney(request:Request, id: str, db: Session = Depends(get_db)):
    return created_all_players(request=request, tourney_id=str(id), db=db)

# @tourney_route.post("/tourney/setting/{profile_id}", response_model=ResultObject, summary="Configure Tourney..")
# def configure_tourney(request:Request, profile_id: str, id: str, lst_categories: List[DominoCategoryCreated]=[], 
#                       settingtourney: SettingTourneyCreated = Depends(), 
#                       image: UploadFile = None, db: Session = Depends(get_db)):
#     return configure_one_tourney(request=request, profile_id=profile_id, tourney_id=id, lst_categories=lst_categories,
#                                  settingtourney=settingtourney.dict(), file=image, db=db)
    
    
# @tourney_route.post("/tourney/setting/{profile_id}", response_model=ResultObject, summary="Configure Tourney..")
# def configure_tourney(request:Request, profile_id: str, id: str, lst_categories: List[DominoCategoryCreated],
#                       settingtourney: SettingTourneyCreated = Depends(), 
#                       image: UploadFile = None, db: Session = Depends(get_db)):
#     return configure_one_tourney(request=request, profile_id=profile_id, tourney_id=id, lst_categories=lst_categories,
#                                  settingtourney=settingtourney.dict(), file=image, db=db)
