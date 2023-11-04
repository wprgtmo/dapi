from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer
from fastapi.responses import FileResponse, JSONResponse
from os import getcwd, remove
from typing import Optional

from domino.schemas.events.events import EventBase
from domino.schemas.events.tourney import TourneyCreated
from domino.schemas.resources.result_object import ResultObject

from domino.services.events.event import get_all, get_all_by_criteria, new, get_one_by_id, delete, update, get_image_event
  
event_route = APIRouter(
    tags=["Events"],
    dependencies=[Depends(JWTBearer())]   
)

@event_route.get("/event", response_model=Dict, summary="Obtain a list of Events.")
def get_events(
    request: Request,
    profile_id: str,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(
        request=request, profile_id=profile_id, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@event_route.get("/event/criteria/", response_model=Dict, summary="Obtain a list of Events by criteria.")
def get_events_by_criteria(
    request: Request,
    profile_id: str,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all_by_criteria(
        request=request, profile_id=profile_id, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@event_route.get("/event/one_event/{id}", response_model=ResultObject, summary="Get a Event for your ID.")
def get_event_by_id(id: str, db: Session = Depends(get_db)):
    return get_one_by_id(event_id=id, db=db)

@event_route.post("/event/{profile_id}", response_model=ResultObject, summary="Create a Event..")
def create_event(request:Request, profile_id: str, event: EventBase = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return new(request=request, profile_id=profile_id, event=event.dict(), db=db, file=image)

@event_route.delete("/event/{id}", response_model=ResultObject, summary="Deactivate a Event by its ID.")
def delete_event(request:Request, id: str, db: Session = Depends(get_db)):
    return delete(request=request, event_id=str(id), db=db)
    
@event_route.put("/event/{id}", response_model=ResultObject, summary="Update a Event by its ID")
def update_event(request:Request, id: str, event: EventBase = Depends(), image: UploadFile = "", db: Session = Depends(get_db)):
    return update(request=request, db=db, event_id=str(id), event=event.dict(), file=image)
