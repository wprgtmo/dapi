# auth.py
from fastapi import Request, HTTPException
from domino.app import _
from domino.models.enterprise.user import Users
from jwt import encode
from domino.auth_bearer import decodeJWT
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domino.schemas.enterprise.user import UserLogin
from fastapi.responses import JSONResponse
from domino.config.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def expire_date(minutes: int):
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    return expire


def write_token(data: dict):
    token = encode(payload={
                   **data, "exp": expire_date(minutes=1440)}, key=settings.secret, algorithm="HS256")
    return token


def get_login_user(request: Request):
    token = request.headers['authorization'].split(' ')[1]
    user = decodeJWT(token)
    return user


def auth(request: Request, db: Session, user: UserLogin):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0]

    str_query = "SELECT us.id user_id, us.username, us.first_name, us.last_name, pro.photo, " +\
        "us.is_active, password, pro.profile_type " +\
        "FROM enterprise.users us inner join enterprise.profile_member pro ON pro.id = us.id " +\
        "WHERE us.username = '" + user.username + "' "
    lst_data = db.execute(str_query)
    if not lst_data:
        raise HTTPException(
            status_code=404, detail=_(locale, "auth.not_found"))

    user_id, username, first_name, last_name, photo, profile_type = '', '', '', '', '', ''
    password = ''
    is_active = False
    for item in lst_data:
        user_id, username = item.user_id, item.username
        first_name, last_name = item.first_name, item.last_name
        photo = item.photo
        is_active = item.is_active
        password = item.password
        profile_type = item.profile_type

    if is_active is False:
        raise HTTPException(status_code=404, detail=_(
            locale, "auth.not_registered"))

    if pwd_context.verify(user.password, password):
        token_data = {"username": username, "user_id": user_id}

        profile = {"user_id": user_id, "first_name": first_name, "last_name": last_name,
                   "photo": get_url_avatar(user_id, photo), "profile_type": profile_type, 
                   "token": write_token(data=token_data)}

        response = JSONResponse(content={
                                "success": True,
                                "message": "Autentificación exitosa",
                                "profile": profile},
                                status_code=200)

        return response
    else:
        raise HTTPException(status_code=404, detail=_(
            locale, "auth.wrong_password"))


def get_url_avatar(user_id: str, file_name: str, api_uri=''):

    api_uri = str(settings.api_uri) if not api_uri else api_uri
    
    photo =  api_uri + "/api/avatar/" + str(user_id) + "/" + file_name if \
        file_name else api_uri + "/api/avatar/user-vector.jpg"

    return photo

def get_url_advertising(tourney_id: str, file_name: str, api_uri=''):

    api_uri = str(settings.api_uri) if not api_uri else api_uri
    table_image = file_name if file_name else "smartdomino.png"
    
    return api_uri + "/api/advertising/" + tourney_id + "/" + table_image

def get_url_smartdomino(api_uri=''):

    api_uri = str(settings.api_uri) if not api_uri else api_uri
    
    return api_uri + "/api/default"