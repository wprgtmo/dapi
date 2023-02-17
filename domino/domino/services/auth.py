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
    token = encode(payload={**data, "exp": expire_date(minutes=30)},
                   key="SECRET_KEY", algorithm="HS256")
    return token


def get_login_user(request: Request):
    token = request.headers['authorization'].split(' ')[1]
    user = decodeJWT(token)
    return user


def auth(request: Request, db: Session, user: UserLogin):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0]

    data = db.query(Users).filter(Users.username == user.username).first()
    if data is None:
        raise HTTPException(
            status_code=404, detail=_(locale, "auth.not_found"))

    if pwd_context.verify(user.password, data.password):
        db_user = db.query(Users).where(
            Users.username == user.username).first()

        token_data = {"username": data.username, "user_id": data.id}

        return JSONResponse(content={"token": write_token(data=token_data), "token_type": "Bearer", "first_name": db_user.first_name, 
                                     "last_name": db_user.last_name, "user_id": db_user.id}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail=_(
            locale, "auth.wrong_password"))
