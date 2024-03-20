from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.enterprise.userprofile import GenericPairProfileCreated
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.enterprise.userprofile import new_profile_pair_player, get_one_pair_profile_by_id, update_one_pair_profile, \
    delete_one_profile, get_all_pair_profile
  
pairprofile_route = APIRouter(
    tags=["Profile"],
    dependencies=[Depends(JWTBearer())]   
)

@pairprofile_route.get("/profile/pairplayer/{profile_id}", response_model=ResultData, summary="Obtain a list of Pair Player profile")
def get_profile(request: Request, profile_id: str, page: int = 1, per_page: int = 6, search: str = "", db: Session = Depends(get_db)):
    return get_all_pair_profile(request=request, profile_id=profile_id, page=page, per_page=per_page, criteria_value=search, db=db)
    
@pairprofile_route.post("/profile/pairplayer/{profile_id}", response_model=ResultObject, summary="Create a Profile of Pair Player")
def create_pair_profile(
    request:Request, profile_id: str, pairprofile: GenericPairProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return new_profile_pair_player(request=request, profile_id=profile_id, pairprofile=pairprofile.dict(), file=image, db=db)

@pairprofile_route.get("/profile/pairplayer/{id}", response_model=ResultObject, summary="Get a Pair Player Profile for your ID.")
def get_pair_profile(request: Request, id: str, db: Session = Depends(get_db)):
    return get_one_pair_profile_by_id(request, id=id, db=db)

@pairprofile_route.delete("/profile/pairplayer/{id}", response_model=ResultObject, summary="Remove Pair player Profile for your ID")
def delete_pair_profile(request:Request, id: str, db: Session = Depends(get_db)):
    return delete_one_profile(request=request, id=str(id), db=db)
    
@pairprofile_route.put("/profile/pairplayer/{id}", response_model=ResultObject, summary="Update Pair Player Profile for your ID")
def update_pair_profile(
    request:Request, id: str, pairprofile: GenericPairProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return update_one_pair_profile(request=request, db=db, id=str(id), pairprofile=pairprofile.dict(), file=image)