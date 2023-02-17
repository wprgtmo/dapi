# Routes user.py

from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.user import UserShema, UserCreate, UserBase, ChagePasswordSchema
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.users import get_all, get_one_by_id, delete, update, change_password
from starlette import status
from domino.auth_bearer import JWTBearer
import uuid

user_route = APIRouter(
    tags=["Users"],
    dependencies=[Depends(JWTBearer())]
)

@user_route.get("/users", response_model=Dict, summary="Get list of Users.")
def get_users(
    request: Request,
    page: int = 1,
    per_page: int = 6,
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@user_route.get("/users/{id}", response_model=ResultObject, summary="Get a User by his ID")
def get_user_by_id(id: str, db: Session = Depends(get_db)):
    return get_one_by_id(user_id=id, db=db)

@user_route.delete("/users/{id}", response_model=ResultObject, summary="Eliminar un Usuario por su ID")
def delete_user(request:Request, id: uuid.UUID, db: Session = Depends(get_db)):
    return delete(request=request, user_id=str(id), db=db)
    
@user_route.put("/users/{id}", response_model=ResultObject, summary="Update a User by his ID.")
def update_user(request:Request, id: uuid.UUID, user: UserCreate, db: Session = Depends(get_db)):
    return update(request=request, db=db, user_id=str(id), user=user)

@user_route.post("/users/password", response_model=ResultObject, summary="Change password to a user.")
def reset_password(
    request: Request,
    password: ChagePasswordSchema,
    db: Session = Depends(get_db)
):
    return change_password(request=request, db=db, password=password)
