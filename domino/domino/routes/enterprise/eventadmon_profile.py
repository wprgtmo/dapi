from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.enterprise.userprofile import EventAdmonProfileCreated
from domino.schemas.resources.result_object import ResultObject

from domino.services.enterprise.userprofile import new_profile_event_admon, get_one_eventadmon_profile_by_id, \
    update_one_event_admon_profile, delete_one_profile
  
eventadmonprofile_route = APIRouter(
    tags=["Profile"],
    dependencies=[Depends(JWTBearer())]   
)

@eventadmonprofile_route.post("/profile/eventadmon", response_model=ResultObject, summary="Create a Profile of Event Admon")
def create_eventadmon_profile(
    request:Request, eventadmonprofile: EventAdmonProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return new_profile_event_admon(request=request, eventadmonprofile=eventadmonprofile.dict(), file=image, db=db)

@eventadmonprofile_route.get("/profile/eventadmon/{id}", response_model=ResultObject, summary="Get a Event Admon Profile for your ID.")
def get_eventadmon_profile(request: Request, id: str, db: Session = Depends(get_db)):
    return get_one_eventadmon_profile_by_id(request, id=id, db=db)

@eventadmonprofile_route.delete("/profile/eventadmon/{id}", response_model=ResultObject, summary="Remove Event Admon Profile for your ID")
def delete_eventadmon_profile(request:Request, id: str, db: Session = Depends(get_db)):
    return delete_one_profile(request=request, id=str(id), db=db)
    
@eventadmonprofile_route.put("/profile/eventadmon/{id}", response_model=ResultObject, summary="Update Event Admon Profile for your ID")
def update_eventadmon_profile(
    request:Request, id: str, eventadmonprofile: EventAdmonProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return update_one_event_admon_profile(request=request, db=db, id=str(id), eventadmonprofile=eventadmonprofile.dict(), file=image)