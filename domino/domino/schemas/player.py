"""coding=utf-8."""

from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional
        
class PlayerBase(BaseModel):
    tourney_id: str
    user_id: str
    nivel: Optional[str]
    
    @validator('tourney_id')
    def tourney_id_not_empty(cls, tourney_id):
        if not tourney_id:
            raise ValueError('Identificador del de Torneo es Requerido')
        return tourney_id
    
    @validator('user_id')
    def user_id_not_empty(cls, user_id):
        if not user_id:
            raise ValueError('Id del usuario es Requerido')
        return user_id
    
class PlayerSchema(PlayerBase):
    
    is_active: bool = True
    
    created_by: str
    created_date: datetime = datetime.today()
    updated_by: str
    updated_date: datetime = datetime.today()
    
    class Config:
        orm_mode = True
