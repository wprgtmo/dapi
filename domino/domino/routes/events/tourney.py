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
  
tourney_route = APIRouter(
    tags=["Tourney"],
    dependencies=[Depends(JWTBearer())]   
)

@tourney_route.get("/tourney/", response_model=Dict, summary="Obtain a list of Tourney.")
def get_tourney(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@tourney_route.get("/tourney/event/{event_id}", response_model=ResultObject, summary="Get List of Tourney for Event.")
def get_by_event(event_id: str, db: Session = Depends(get_db)):
    return get_all_by_event_id(event_id=event_id, db=db)

@tourney_route.get("/tourney/one/{id}", response_model=ResultObject, summary="Get a Tourney for your ID.")
def get_tourney_by_id(id: str, db: Session = Depends(get_db)):
    return get_one_by_id(tourney_id=id, db=db)

@tourney_route.post("/tourney", response_model=ResultObject, summary="Create a Tourney..")
def create_tourney(request:Request, event_id: str, tourney: TourneyCreated, db: Session = Depends(get_db)):
    return new(request=request, event_id=event_id, tourney=tourney, db=db)

@tourney_route.delete("/tourney/{id}", response_model=ResultObject, summary="Deactivate a Tourney by its ID.")
def delete_tourney(request:Request, id: str, db: Session = Depends(get_db)):
    return delete(request=request, tourney_id=str(id), db=db)
    
@tourney_route.put("/tourney/{id}", response_model=ResultObject, summary="Update a Tourney by its ID")
def update_tourney(request:Request, id: str, tourney: TourneyCreated, db: Session = Depends(get_db)):
    return update(request=request, db=db, tourney_id=id, tourney=tourney)

@tourney_route.post("/tourney/setting/tables/{id}", response_model=ResultObject, summary="Get amount tables")
def amount_tables(id: str, db: Session = Depends(get_db)):
    return get_amount_tables(tourney_id=id, db=db)

@tourney_route.post("/tourney/setting/{profile_id}", response_model=ResultObject, summary="Configure Tourney..")
def configure_tourney(request:Request, profile_id: str, id: str, settingtourney: SettingTourneyCreated = Depends(), 
                      image: UploadFile = None, db: Session = Depends(get_db)):
    return configure_one_tourney(request=request, profile_id=profile_id, tourney_id=id,
                                 settingtourney=settingtourney.dict(), file=image, db=db)


