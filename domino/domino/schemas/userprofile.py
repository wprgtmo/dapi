"""coding=utf-8."""
 
from pydantic import BaseModel, ValidationError, validator 
from datetime import datetime, date
from uuid import UUID
from datetime import date
from typing import Optional, List
from domino.app import _
        
class ProfileMemberBase(BaseModel):
    name: str
    email: Optional[str]
    profile_type: Optional[str]
    city_id: Optional[int]
    photo: Optional[str]
    
    receive_notifications: Optional[bool] = False
    
class ProfileMemberSchema(ProfileMemberBase):
    id: Optional[int]
    
    created_by: str
    created_date: datetime = datetime.today()
    updated_by: str
    updated_date: datetime = datetime.today()
    
    is_active: bool = True
    is_ready: bool = True
    
    class Config:
        orm_mode = True    
    
class ProfileUsersBase(BaseModel):
    profile_id: str
    username: str
    is_principal: Optional[bool] = False
    
class ProfileUsersSchema(ProfileUsersBase):
    
    created_by: str
    created_date: datetime = datetime.today()
    
    class Config:
        orm_mode = True 
    

class ProfileSinglePlayerBase(BaseModel):
    profile_id: str
    elo: int
    ranking: str
    
class ProfileSinglePlayerSchema(ProfileSinglePlayerBase):
    
    class Config:
        orm_mode = True 
        
class SingleProfileCreated(BaseModel):
    name: str
    email: Optional[str]
    city_id: Optional[int]
    
    receive_notifications: Optional[bool] = False
