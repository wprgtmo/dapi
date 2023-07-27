# Routes pais.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from domino.app import get_db

from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.resources.country import CountryBase, CountrySchema
from domino.schemas.resources.result_object import ResultObject
  
from domino.services.resources.country import new, get_one_by_id, delete, update
  
country_route = APIRouter(
    tags=["Nomenclators"],  # tags=["Countries"],
    dependencies=[Depends(JWTBearer())]   
)

@country_route.post("/countries", response_model=ResultObject, summary="Create a country")
def create_country(request:Request, country: CountryBase, db: Session = Depends(get_db)):
    return new(request=request, country=country, db=db)

@country_route.get("/countries/{id}", response_model=ResultObject, summary="Get a Country for your ID.")
def get_country_by_id(request:Request, id: int, db: Session = Depends(get_db)):
    return get_one_by_id(request, country_id=id, db=db)

@country_route.delete("/countries/{id}", response_model=ResultObject, summary="Remove country for your ID")
def delete_country(request:Request, id: int, db: Session = Depends(get_db)):
    return delete(request=request, country_id=str(id), db=db)
    
@country_route.put("/countries/{id}", response_model=ResultObject, summary="Update country for your ID")
def update_country(request:Request, id: int, country: CountryBase, db: Session = Depends(get_db)):
    return update(request=request, db=db, country_id=str(id), country=country)
