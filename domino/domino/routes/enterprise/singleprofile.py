from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.enterprise.userprofile import SingleProfileCreated, GenericSingleProfileCreated
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.enterprise.userprofile import get_all_single_profile, new_profile_single_player, get_one_single_profile, update_one_single_profile, delete_one_profile
 
singleprofile_route = APIRouter(
    tags=["Profile"],
    dependencies=[Depends(JWTBearer())]   
)

@singleprofile_route.get("/profile/singleplayer/{profile_id}", response_model=ResultData, summary="Obtain a list of Single Player profile")
def get_profile(request: Request, profile_id: str, page: int = 1, per_page: int = 6, search: str = "", db: Session = Depends(get_db)):
    return get_all_single_profile(request=request, profile_id=profile_id, page=page, per_page=per_page, criteria_value=search, db=db)

@singleprofile_route.get("/profile/singleplayer/one/{id}", response_model=ResultObject, summary="Get a Single Profile of Player for your ID.")
def get_single_profile(request: Request, id: str, db: Session = Depends(get_db)):
    return get_one_single_profile(request, id=id, db=db)
    
@singleprofile_route.post("/profile/singleplayer/{profile_id}", response_model=ResultObject, summary="Create a Single Profile of Player")
def create_single_profile(request:Request, profile_id: str, singleprofile: GenericSingleProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return new_profile_single_player(request=request, profile_id=profile_id, singleprofile=singleprofile.dict(), file=image, db=db)

@singleprofile_route.delete("/profile/singleplayer/{id}", response_model=ResultObject, summary="Remove Single Profile for your ID")
def delete_single_profile(request:Request, id: str, db: Session = Depends(get_db)):
    return delete_one_profile(request=request, id=str(id), db=db)
    
@singleprofile_route.put("/profile/singleplayer/{id}", response_model=ResultObject, summary="Update Single Profile for your ID")
def update_single_profile(request:Request, id: str, singleprofile: GenericSingleProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return update_one_single_profile(request=request, db=db, id=str(id), singleprofile=singleprofile.dict(), file=image)
