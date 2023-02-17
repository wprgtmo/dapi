# Routes ciudad.py
from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.city import CityBase, CitySchema, CityCreate
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from domino.services.city import get_all, new, get_one_by_id, delete, update
from starlette import status
from domino.auth_bearer import JWTBearer
  
city_route = APIRouter(
    tags=["Cities"],
    dependencies=[Depends(JWTBearer())]   
)

@city_route.get("/city", response_model=Dict, summary="Get list of Cities")
def get_cities(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@city_route.get("/city/{id}", response_model=ResultObject, summary="Get one city for your ID.")
def get_city_by_id(id: int, db: Session = Depends(get_db)):
    return get_one_by_id(city_id=id, db=db)

@city_route.post("/city", response_model=ResultObject, summary="Create a City.")
def create_city(request:Request, city: CityCreate, db: Session = Depends(get_db)):
    return new(request, city=city, db=db)

@city_route.delete("/city/{id}", response_model=ResultObject, summary="Remove a City.")
def delete_city(request:Request, id: int, db: Session = Depends(get_db)):
    return delete(request=request, city_id=str(id), db=db)
    
@city_route.put("/city/{id}", response_model=ResultObject, summary="Update a city for your ID")
def update_city(request:Request, id: int, city: CityCreate, db: Session = Depends(get_db)):
    return update(request=request, db=db, city_id=str(id), city=city)
