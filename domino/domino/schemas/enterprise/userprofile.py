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
    
    single_profile_id: str
    
class ProfileUsersSchema(ProfileUsersBase):
    
    created_by: str
    created_date: datetime = datetime.today()
    
    class Config:
        orm_mode = True 
    

class ProfileSinglePlayerBase(BaseModel):
    profile_id: str
    elo: int
    ranking: str
    level: str
    
class ProfileSinglePlayerSchema(ProfileSinglePlayerBase):
    
    class Config:
        orm_mode = True 
        
class SingleProfileCreated(BaseModel):
    name: str
    email: Optional[str]
    city_id: Optional[int]
    
    level: Optional[str]
    
    receive_notifications: Optional[bool] = False
    

class DefaultUserProfileBase(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    sex: Optional[str]
    birthdate: Optional[date]
    alias: Optional[str]
    job: Optional[str]
    city_id: Optional[int]
    
    email: Optional[str]
    phone: Optional[str]
    
    receive_notifications: Optional[bool] = False
    
    class Config:
        orm_mode = True
 
# class UserRankin(BaseModel):
#     username: str
#     elo: int
#     ranking: str


class ProfilePairPlayerBase(BaseModel):
    profile_id: str
    level: Optional[str]
    
class ProfilePairPlayerSchema(ProfilePairPlayerBase):
    
    class Config:
        orm_mode = True 
        
class PairProfileCreated(BaseModel):
    name: str
    email: Optional[str]
    level: Optional[str]
    city_id: Optional[int]
    
    receive_notifications: Optional[bool] = False
    
    other_profile_id: Optional[str]
    
class ProfileTeamPlayerBase(BaseModel):
    profile_id: str
    level: Optional[str]
    amount_members: int
    
class ProfileTeamPlayerSchema(ProfileTeamPlayerBase):
    
    class Config:
        orm_mode = True 
        
class TeamProfileCreated(BaseModel):
    name: str
    email: Optional[str]
    level: Optional[str]
    city_id: Optional[int]
    # amount_members: int
    
    receive_notifications: Optional[bool] = False
    
    others_profile_id: Optional[str]
class ProfileRefereeBase(BaseModel):
    profile_id: str
    level: Optional[str]
    
class ProfileRefereeSchema(ProfileRefereeBase):
    
    class Config:
        orm_mode = True 
        
class RefereeProfileCreated(BaseModel):
    name: str
    email: Optional[str]
    level: Optional[str]
    city_id: Optional[int]
    
    receive_notifications: Optional[bool] = False
    
    

class ProfileFollowersBase(BaseModel):
    profile_id: str
    profile_follow_id: str
    
class ProfileFollowersSchema(ProfileFollowersBase):
    
    username: str
    username_follow: str
    
    created_by: str
    created_date: datetime = datetime.today()
    
    is_active: bool = True
    
    class Config:
        orm_mode = True 
