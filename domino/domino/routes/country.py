# Routes pais.py
from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.country import CountryBase, CountrySchema
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from domino.services.country import new, get_one_by_id, delete, update
from starlette import status
from domino.auth_bearer import JWTBearer
  
country_route = APIRouter(
    tags=["Country"],
    dependencies=[Depends(JWTBearer())]   
)

@country_route.get("/country/{id}", response_model=ResultObject, summary="Get a Country for your ID.")
def get_country_by_id(request:Request, id: int, db: Session = Depends(get_db)):
    return get_one_by_id(request, country_id=id, db=db)

@country_route.delete("/country/{id}", response_model=ResultObject, summary="Remove country for your ID")
def delete_country(request:Request, id: int, db: Session = Depends(get_db)):
    return delete(request=request, country_id=str(id), db=db)
    
@country_route.put("/country/{id}", response_model=ResultObject, summary="Update country for your ID")
def update_country(request:Request, id: int, country: CountryBase, db: Session = Depends(get_db)):
    return update(request=request, db=db, country_id=str(id), country=country)
