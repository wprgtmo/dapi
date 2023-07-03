from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from domino.schemas.userprofile import DefaultUserProfileBase
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from domino.services.userprofile import new_profile_single_player, get_one_single_profile, update_one_single_profile, delete_one_single_profile, \
    new_profile_default_user, get_one_default_user_profile, update_one_default_profile, delete_one_default_profile

from starlette import status
from domino.auth_bearer import JWTBearer
  
defaultprofile_route = APIRouter(
    tags=["DefaultProfile"],
    dependencies=[Depends(JWTBearer())]   
)

@defaultprofile_route.post("/defaultprofile", response_model=ResultObject, summary="Create a Default User Profile")
def create_single_profile(request:Request, defaultusereprofile: DefaultUserProfileBase = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return new_profile_default_user(request=request, defaultusereprofile=defaultusereprofile.dict(), file=image, db=db)

@defaultprofile_route.get("/defaultprofile/one/{id}", response_model=ResultObject, summary="Get a SDefault User Profile for your ID.")
def get_default_profile(request: Request, id: str, db: Session = Depends(get_db)):
    return get_one_default_user_profile(request, id=id, db=db)

@defaultprofile_route.delete("/defaultprofile/{id}", response_model=ResultObject, summary="Remove Default User Profile for your ID")
def delete_default_profile(request:Request, id: str, db: Session = Depends(get_db)):
    return delete_one_default_profile(request=request, id=str(id), db=db)
    
@defaultprofile_route.put("/defaultprofile/{id}", response_model=ResultObject, summary="Update Default User Profile for your ID")
def update_default_profile(request:Request, id: str, defaultusereprofile: DefaultUserProfileBase = Depends(), image: UploadFile = None, db: Session = Depends(get_db)):
    return update_one_default_profile(request=request, db=db, id=str(id), defaultusereprofile=defaultusereprofile.dict(), file=image)

@defaultprofile_route.put("/users/{id}", response_model=ResultObject, summary="Update a User by his ID.")
def update_user(request:Request, id: uuid.UUID, user: UserProfile = Depends(), avatar: UploadFile = None, db: Session = Depends(get_db)):
    return update_one_profile(request=request, db=db, user_id=str(id), user=user, avatar=avatar)

@defaultprofile_route.get("/profile/{id}", response_model=ResultObject, summary="Get Profile a User by his ID")
def get_profile(
    request: Request,
    id: str, 
    db: Session = Depends(get_db)
):
    return get_one_profile(request, user_id=id, db=db)


# @auth_routes.post("/register", response_model=ResultObject, tags=["Autentificación"], summary="Register a user on the platform")
# def create_user(request: Request, user: UserCreate = Depends(), avatar: UploadFile = None, db: Session = Depends(get_db)):
#     return new_user(request=request, user=user, db=db, avatar=avatar)