"""coding=utf-8."""
 
from pydantic import BaseModel, ValidationError, validator 
from uuid import UUID
from datetime import date
from typing import Optional
from domino.app import _
 
class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    country_id: Optional[int]

    @validator('username')
    def username_not_empty(cls, username):
        if not username:
            raise ValueError('Nombre de usuario es requerido')
        return username
    
    @validator('first_name')
    def first_name_not_empty(cls, first_name):
        if not first_name:
            raise ValueError('Nombre del Usuario es Requerido')
        return first_name

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(UserBase):
    password: str 
    
    @validator('password')
    def password_not_empty(cls, password):
        if not password:
            raise ValueError('Contraseña es Requerido')
        return password 

class UserShema(UserCreate):
    id: UUID
    is_active: bool
    
    class Config:
        orm_mode = True
    
class ChagePasswordSchema(BaseModel):
    username: Optional[str]
    current_password: str
    new_password: str
    renew_password: str
    
    @validator('current_password')
    def current_password_not_empty(cls, current_password):
        if not current_password:
            raise ValueError('Contraseña Actual es Requerido')
        return current_password
    
    @validator('current_password')
    def new_password_not_empty(cls, new_password):
        if not new_password:
            raise ValueError('Contraseña Nueva es Requerido')
        return new_password
    
    @validator('renew_password')
    def renew_password_password_not_empty(cls, renew_password):
        if not renew_password:
            raise ValueError('Contraseña Nueva repetida es Requerida')
        return renew_password 

class UserProfile(UserBase):
    sex: Optional[str]
    birthdate: Optional[date]
    alias: Optional[str]
    job: Optional[str]
    photo: Optional[str]
    city_id: Optional[int]
    
    class Config:
        orm_mode = True
 
class UserRankin(BaseModel):
    username: str
    elo: int
    ranking: str
 