from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from domino.schemas.events import EventBase
from domino.schemas.tourney import TourneyCreated
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.event import get_all, new, get_one_by_id, delete, update, get_image_event
from starlette import status
from domino.auth_bearer import JWTBearer
from fastapi.responses import FileResponse, JSONResponse
from os import getcwd, remove
  
event_route = APIRouter(
    tags=["Events"],
    dependencies=[Depends(JWTBearer())]   
)

@event_route.get("/event", response_model=Dict, summary="Obtain a list of Events.")
def get_events(
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
def create_event(request:Request, event: EventBase = Depends(), image: UploadFile = File(...), db: Session = Depends(get_db)):
    return new(request=request, event=event.dict(), db=db, file=image)

@event_route.delete("/event/{id}", response_model=ResultObject, summary="Deactivate a Event by its ID.")
def delete_event(request:Request, id: str, db: Session = Depends(get_db)):
    return delete(request=request, event_id=str(id), db=db)
    
@event_route.put("/event/{id}", response_model=ResultObject, summary="Update a Event by its ID")
def update_event(request:Request, id: str, event: EventBase = Depends(), image: UploadFile = File(...), db: Session = Depends(get_db)):
    return update(request=request, db=db, event_id=str(id), event=event.dict(), file=image)

@event_route.get("/event/{event_id}", summary="Mostrar imagen de un evento")
def getEventImage(event_id: str, db: Session = Depends(get_db)):
    return get_image_event(event_id, db=db)
    
    # return FileResponse(getcwd() + "/public/events/" + user_id + "/" + file_name)

@event_route.delete("/delete/{name}")
def delevent(name: str):
    try:
        remove(getcwd() + "/public/events/" + name)
        return JSONResponse(content={"success": True, "message": "file deleted"}, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={"success": False}, status_code=404)