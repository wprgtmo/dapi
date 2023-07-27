"""coding=utf-8."""

from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional
        
class SponsorBase(BaseModel):
    event_id: str
    user_id: str
    
    @validator('tourney_id')
    def event_id_not_empty(cls, event_id):
        if not event_id:
            raise ValueError('Identificador del Evento es Requerido')
        return event_id
    
    @validator('user_id')
    def user_id_not_empty(cls, user_id):
        if not user_id:
            raise ValueError('Id del usuario es Requerido')
        return user_id
    
class SponsorSchema(SponsorBase):
    
    is_active: bool = True
    
    created_by: str
    created_date: datetime = datetime.today()
    updated_by: str
    updated_date: datetime = datetime.today()
    
    class Config:
        orm_mode = True