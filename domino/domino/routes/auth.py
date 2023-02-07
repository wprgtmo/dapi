# auth.py

from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.user import UserLogin
from domino.services.auth import auth 
#, get_captcha, verify_captcha

from sqlalchemy.orm import Session
from domino.app import get_db
from starlette import status

auth_routes = APIRouter()

# @auth_routes.get('/captcha/show', tags=["Captcha"], summary='Mostrar un captcha al usuario')
# def captcha(request: Request):
#     return get_captcha(request)   

# @auth_routes.post('/captcha/verify', status_code=status.HTTP_200_OK, tags=["Captcha"], summary='Verificar el captcha del usuario')
# def captcha(request: Request, text: str):
#     is_captcha = verify_captcha(request=request, text=text)
#     if is_captcha:
#         raise HTTPException(status_code=200, detail="Captcha Correcto")
#     else:
#         raise HTTPException(status_code=403, detail="Captcha Incorrecto")    

@auth_routes.post("/login", status_code=status.HTTP_200_OK, tags=["Autentificación"], summary="Autentificación en la API")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return auth(db=db, user=user)