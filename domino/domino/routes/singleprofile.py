from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from domino.schemas.userprofile import SingleProfileCreated
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from domino.services.userprofile import new_profile_single_player, get_one_single_profile, update_one_single_profile, delete_one_single_profile
from starlette import status
from domino.auth_bearer import JWTBearer
  
singleprofile_route = APIRouter(
    tags=["Profile"],
    dependencies=[Depends(JWTBearer())]   
)

@singleprofile_route.post("/profile/single", response_model=ResultObject, summary="Create a Single Profile of Player")
def create_single_profile(request:Request, singleprofile: SingleProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return new_profile_single_player(request=request, singleprofile=singleprofile.dict(), file=image, db=db)

@singleprofile_route.get("/profile/single/{id}", response_model=ResultObject, summary="Get a Single Profile of Player for your ID.")
def get_single_profile(request: Request, id: str, db: Session = Depends(get_db)):
    return get_one_single_profile(request, id=id, db=db)

@singleprofile_route.delete("/profile/single/{id}", response_model=ResultObject, summary="Remove Single Profile for your ID")
def delete_single_profile(request:Request, id: str, db: Session = Depends(get_db)):
    return delete_one_single_profile(request=request, id=str(id), db=db)
    
@singleprofile_route.put("/profile/single/{id}", response_model=ResultObject, summary="Update Single Profile for your ID")
def update_single_profile(request:Request, id: str, singleprofile: SingleProfileCreated = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return update_one_single_profile(request=request, db=db, id=str(id), singleprofile=singleprofile.dict(), file=image)
