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

from domino.app import _

auth_routes = APIRouter()

@auth_routes.post("/login", status_code=status.HTTP_200_OK, tags=["Autentificación"], summary="Autentificación en la API")
def login(request:Request, user: UserLogin, db: Session = Depends(get_db)):
    return auth(request=request, db=db, user=user)

@auth_routes.get('/me', summary="Obtiene información del usuario autentificado", tags=["Autentificación"], dependencies=[Depends(JWTBearer())])
async def get_me(request:Request):
    user = get_current_user(request)       
    return JSONResponse(content=user, status_code=200)
