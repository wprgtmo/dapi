"""coding=utf-8."""
 
from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional, List


class InvitationBase(BaseModel):
    tourney_id: str
    user_name: str
    rolevent_name: str
    modality: str
    
    @validator('tourney_id')
    def tourney_id_not_empty(cls, tourney_id):
        if not tourney_id:
            raise ValueError('Identificador del torneo es Requerido')
        return tourney_id
    
    @validator('user_name')
    def user_name_not_empty(cls, user_name):
        if not user_name:
            raise ValueError('Nombre de usuario es Requerida')
        return user_name
    
class InvitationSchema(InvitationBase):
    id: Optional[int]
    
    status_name: str = 'SENT'
    created_by: str
    created_date: datetime = datetime.today()
    updated_by: str
    updated_date: datetime = datetime.today()
    
    class Config:
        orm_mode = True
        
class InvitationAccepted(BaseModel):
    accept: bool = True
        
        
class InvitationFilters(BaseModel):
    player: Optional[str]
    country: Optional[str]
    elo_min: Optional[float]
    elo_max: Optional[float]