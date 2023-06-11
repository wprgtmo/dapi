"""coding=utf-8."""
 
from pydantic import BaseModel, ValidationError, validator 
from datetime import datetime, date
from uuid import UUID
from datetime import date
from typing import Optional, List
from domino.app import _
        
class MemberProfileBase(BaseModel):
    name: str
    email: Optional[str]
    rolevent_name: Optional[str]
    modality: Optional[str]
    city_id: Optional[int]
    photo: Optional[str]
    
    
class MemberProfileSchema(MemberProfileBase):
    id: Optional[int]
    
    created_by: str
    created_date: datetime = datetime.today()
    updated_by: str
    updated_date: datetime = datetime.today()
    
    is_active: bool = True
    is_ready: bool = True
    
    class Config:
        orm_mode = True    
    
class MemberUsersBase(BaseModel):
    profile_id: str
    username: str
    is_principal: Optional[bool] = False
    
class MemberUsersSchema(MemberUsersBase):
    
    created_by: str
    created_date: datetime = datetime.today()
    
    class Config:
        orm_mode = True 
    