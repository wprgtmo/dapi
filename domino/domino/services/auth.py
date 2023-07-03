# auth.py
from fastapi import Request, HTTPException
from domino.app import _
from domino.models.user import Users
from jwt import encode
from domino.auth_bearer import decodeJWT
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domino.schemas.user import UserLogin
from fastapi.responses import JSONResponse
from domino.config.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def expire_date(minutes: int):
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    return expire


def write_token(data: dict):
    token = encode(payload={**data, "exp": expire_date(minutes=1440)}, key="SECRET_KEY", algorithm="HS256")
    return token


def get_login_user(request: Request):
    token = request.headers['authorization'].split(' ')[1]
    user = decodeJWT(token)
    return user


def auth(request: Request, db: Session, user: UserLogin):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0]
    
    str_query = "SELECT us.id user_id, us.username, us.first_name, us.last_name, pro.photo, " +\
        "us.is_active, password " +\
        "FROM enterprise.users us inner join enterprise.profile_member pro ON pro.id = us.id " +\
        "WHERE us.username = '" + user.username + "' "
    lst_data = db.execute(str_query)
    if not lst_data:
        raise HTTPException(status_code=404, detail=_(locale, "auth.not_found"))

    user_id, username, first_name, last_name, photo = '', '', '', '', ''
    password = ''
    is_active = False
    for item in lst_data:
        user_id, username = item.user_id, item.username
        first_name, last_name= item.first_name, item.last_name
        photo = item.photo
        is_active = item.is_active
        password = item.password
        
    if is_active is False:
        raise HTTPException(status_code=404, detail=_(locale, "auth.not_registered"))
        
    if pwd_context.verify(user.password, password):
        token_data = {"username": username, "user_id": user_id}
        
        return JSONResponse(content={"token": write_token(data=token_data), 
                                     "token_type": "Bearer", 
                                     "first_name": first_name, 
                                     "last_name": last_name, 
                                     "photo": get_url_avatar(user_id, photo),  
                                     "user_id": user_id}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail=_(locale, "auth.wrong_password"))

def get_url_avatar(user_id: str, file_name: str, host='', port=''):
    
    host=str(settings.server_uri) if not host else host
    port=str(int(settings.server_port)) if not port else port
    
    photo = "http://" + host + ":" + port + "/api/avatar/" + str(user_id) + "/" + file_name if \
        file_name else "http://" + host + ":" + port + "/api/avatar/user-vector.jpg"
        
    return photo