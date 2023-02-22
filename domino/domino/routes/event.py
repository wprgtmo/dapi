from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.events import EventBase
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.event import get_all, new, get_one_by_id, delete, update
from starlette import status
from domino.auth_bearer import JWTBearer
  
event_route = APIRouter(
    tags=["Events"],
    dependencies=[Depends(JWTBearer())]   
)

@event_route.get("/event", response_model=Dict, summary="Obtain a list of Events.")
def get_post(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@event_route.get("/event/{id}", response_model=ResultObject, summary="Get a Event for your ID.")
def get_event_by_id(id: str, db: Session = Depends(get_db)):
    return get_one_by_id(event_id=id, db=db)

@event_route.post("/event", response_model=ResultObject, summary="Create a Event..")
def create_event(request:Request, event: EventBase, db: Session = Depends(get_db)):
    return new(request=request, event=event, db=db)

@event_route.delete("/event/{id}", response_model=ResultObject, summary="Deactivate a Event by its ID.")
def delete_event(request:Request, id: int, db: Session = Depends(get_db)):
    return delete(request=request, event_id=str(id), db=db)
    
@event_route.put("/event/{id}", response_model=ResultObject, summary="Update a Event by its ID")
def update_event(request:Request, id: int, event: EventBase, db: Session = Depends(get_db)):
    return update(request=request, db=db, event_id=str(id), event=event)