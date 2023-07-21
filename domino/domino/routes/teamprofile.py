from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from domino.schemas.userprofile import TeamProfileCreated
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from domino.services.userprofile import new_profile_team_player, get_one_team_profile_by_id, update_one_team_profile, delete_one_profile
from starlette import status
from domino.auth_bearer import JWTBearer
  
teamprofile_route = APIRouter(
    tags=["Profile"],
    dependencies=[Depends(JWTBearer())]   
)

@teamprofile_route.post("/profile/team", response_model=ResultObject, summary="Create a Profile of Team Player")
def create_team_profile(
    request:Request, teamprofile: TeamProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return new_profile_team_player(request=request, teamprofile=teamprofile.dict(), file=image, db=db)

@teamprofile_route.get("/profile/team/{id}", response_model=ResultObject, summary="Get a Team Player Profile for your ID.")
def get_team_profile(request: Request, id: str, db: Session = Depends(get_db)):
    return get_one_team_profile_by_id(request, id=id, db=db)

@teamprofile_route.delete("/profile/team/{id}", response_model=ResultObject, summary="Remove Team player Profile for your ID")
def delete_team_profile(request:Request, id: str, db: Session = Depends(get_db)):
    return delete_one_profile(request=request, id=str(id), db=db)
    
@teamprofile_route.put("/profile/team/{id}", response_model=ResultObject, summary="Update Team Player Profile for your ID")
def update_team_profile(
    request:Request, id: str, teamprofile: TeamProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return update_one_team_profile(request=request, db=db, id=str(id), teamprofile=teamprofile.dict(), file=image)