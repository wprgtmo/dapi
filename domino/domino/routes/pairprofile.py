from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from domino.schemas.userprofile import PairProfileCreated
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from domino.services.userprofile import new_profile_pair_player, get_one_pair_profile, update_one_pair_profile, delete_one_profile
from starlette import status
from domino.auth_bearer import JWTBearer
  
pairprofile_route = APIRouter(
    tags=["Profile"],
    dependencies=[Depends(JWTBearer())]   
)

@pairprofile_route.post("/profile/pair", response_model=ResultObject, summary="Create a Profile of Pair Player")
def create_pair_profile(
    request:Request, paireprofile: PairProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return new_profile_pair_player(request=request, paireprofile=paireprofile.dict(), file=image, db=db)

@pairprofile_route.get("/profile/pair/{id}", response_model=ResultObject, summary="Get a Pair Player Profile for your ID.")
def get_pair_profile(request: Request, id: str, db: Session = Depends(get_db)):
    return get_one_pair_profile(request, id=id, db=db)

@pairprofile_route.delete("/profile/pair/{id}", response_model=ResultObject, summary="Remove Pair player Profile for your ID")
def delete_pair_profile(request:Request, id: str, db: Session = Depends(get_db)):
    return delete_one_profile(request=request, id=str(id), db=db)
    
@pairprofile_route.put("/profile/pair/{id}", response_model=ResultObject, summary="Update Pair Player Profile for your ID")
def update_pair_profile(
    request:Request, id: str, pairprofile: PairProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return update_one_pair_profile(request=request, db=db, id=str(id), pairprofile=pairprofile.dict(), file=image)