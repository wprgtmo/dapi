from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from domino.schemas.userprofile import RefereeProfileCreated
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from domino.services.userprofile import new_profile_referee, get_one_referee_profile, update_one_referee_profile, delete_one_profile
from starlette import status
from domino.auth_bearer import JWTBearer
  
refereeprofile_route = APIRouter(
    tags=["Profile"],
    dependencies=[Depends(JWTBearer())]   
)

@refereeprofile_route.post("/profile/referee", response_model=ResultObject, summary="Create a Profile of Referee")
def create_referee_profile(
    request:Request, refereeprofile: RefereeProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return new_profile_referee(request=request, refereeprofile=refereeprofile.dict(), file=image, db=db)

@refereeprofile_route.get("/profile/referee/{id}", response_model=ResultObject, summary="Get a Referee Profile for your ID.")
def get_referee_profile(request: Request, id: str, db: Session = Depends(get_db)):
    return get_one_referee_profile(request, id=id, db=db)

@refereeprofile_route.delete("/profile/referee/{id}", response_model=ResultObject, summary="Remove Referee Profile for your ID")
def delete_referee_profile(request:Request, id: str, db: Session = Depends(get_db)):
    return delete_one_profile(request=request, id=str(id), db=db)
    
@refereeprofile_route.put("/profile/referee/{id}", response_model=ResultObject, summary="Update Referee Profile for your ID")
def update_referee_profile(
    request:Request, id: str, refereeprofile: RefereeProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return update_one_referee_profile(request=request, db=db, id=str(id), refereeprofile=refereeprofile.dict(), file=image)