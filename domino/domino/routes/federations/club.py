# Routes federation.py
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict

from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.federations.federations import ClubsBase
from domino.schemas.resources.result_object import ResultObject

from domino.services.federations.clubs import new, update, delete, get_all, get_one_by_id, get_all_by_federation, save_logo_club
  
club_route = APIRouter(
    tags=["Nomenclators"],  # tags=["Countries"],
    dependencies=[Depends(JWTBearer())]   
)

@club_route.get("/club", response_model=Dict, summary="Obtain a list of Clubs.")
def get_clubs(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    search: str = "",
    db: Session = Depends(get_db)
):
    return get_all(
        request=request, page=page, per_page=per_page, criteria_value=search, db=db)

@club_route.get("/club/federation/{id}", response_model=ResultObject, summary="Obtain a list of Clubs.")
def get_clubs_by_federation(request: Request, id=id, db: Session = Depends(get_db)):
    return get_all_by_federation(request=request, federation_id=id, db=db)
        
@club_route.post("/club", response_model=ResultObject, summary="Create new Club")
def create_club(request:Request, club: ClubsBase = Depends(), logo: UploadFile = None, db: Session = Depends(get_db)):
    return new(request=request, club=club.dict(), logo=logo, db=db)

@club_route.get("/club/one/{id}", response_model=ResultObject, summary="Get a Club for your ID.")
def get_club_by_id(request:Request, id: int, db: Session = Depends(get_db)):
    return get_one_by_id(request, club_id=id, db=db)

@club_route.delete("/club/{id}", response_model=ResultObject, summary="Remove Club for your ID")
def delete_club(request:Request, id: int, db: Session = Depends(get_db)):
    return delete(request=request, club_id=str(id), db=db)
    
@club_route.put("/club/{id}", response_model=ResultObject, summary="Update Club for your ID")
def update_club(request:Request, id: int, club: ClubsBase = Depends(), logo: UploadFile = None, db: Session = Depends(get_db)):
    return update(request=request, db=db, club_id=str(id), club=club.dict(), logo=logo)
