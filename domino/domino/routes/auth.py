# auth.py

from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.user import UserLogin
from domino.services.auth import auth

from sqlalchemy.orm import Session
from domino.app import get_db
from starlette import status

from domino.auth_bearer import JWTBearer
from domino.functions_jwt import get_current_user
from fastapi.responses import JSONResponse

from domino.schemas.result_object import ResultObject, ResultData
from domino.schemas.user import UserCreate
from domino.schemas.country import CountryBase
from typing import Dict
from domino.services.users import new as new_user
from domino.services.country import new as new_country
from domino.services.country import get_all

from domino.app import _

auth_routes = APIRouter()


@auth_routes.post("/login", status_code=status.HTTP_200_OK, tags=["Autentificación"], summary="Autentificación en la API")
def login(request: Request, user: UserLogin, db: Session = Depends(get_db)):
    return auth(request=request, db=db, user=user)


@auth_routes.get('/me', summary="Obtiene información del usuario autentificado", tags=["Autentificación"], dependencies=[Depends(JWTBearer())])
async def get_me(request: Request):
    user = get_current_user(request)
    return JSONResponse(content=user, status_code=200)


@auth_routes.post("/register", response_model=ResultObject, tags=["Autentificación"], summary="Register a user on the platform")
def create_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    return new_user(request=request, user=user, db=db)

@auth_routes.post("/nomenclators", response_model=ResultObject, tags=["Nomenclators"], summary="Create a country")
def create_country(request:Request, country: CountryBase, db: Session = Depends(get_db)):
    return new_country(request=request, country=country, db=db)

@auth_routes.get("/nomenclators", response_model=Dict, tags=["Nomenclators"], summary="Get list of Countries")
def get_country(
    request: Request,
    page: int = 0, 
    per_page: int = 0, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)
