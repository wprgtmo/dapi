"""coding=utf-8."""

from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional
        
class PlayerBase(BaseModel):
    tourney_id: str
    profile_id: str
    nivel: Optional[str]
    invitation_id: Optional[str]
    
    @validator('tourney_id')
    def tourney_id_not_empty(cls, tourney_id):
        if not tourney_id:
            raise ValueError('Identificador del de Torneo es Requerido')
        return tourney_id
    
    @validator('profile_id')
    def profile_id_not_empty(cls, profile_id):
        if not profile_id:
            raise ValueError('Id del profile de usario es Requerido')
        return profile_id
    
class PlayerSchema(PlayerBase):
    
    id: Optional[int]
    is_active: bool = True
    
    created_by: str
    created_date: datetime = datetime.today()
    updated_by: str
    updated_date: datetime = datetime.today()
    
    class Config:
        orm_mode = True
