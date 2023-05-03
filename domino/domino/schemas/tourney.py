"""coding=utf-8."""

from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional, List

 
class TourneyBase(BaseModel):
    name: str
    event_id: str
    modality: Optional[str]
    summary: Optional[str]
    
    start_date: Optional[date] = date.today()
    
    @validator('name')
    def name_not_empty(cls, name):
        if not name:
            raise ValueError('Nombre de Torneo es Requerido')
        return name
    
    @validator('event_id')
    def event_id_not_empty(cls, event_id):
        if not event_id:
            raise ValueError('Id del Evento es Requerida')
        return event_id
    
    @validator('modality')
    def modality_not_empty(cls, modality):
        if not modality:
            raise ValueError('Modalidad del torneo es Requerida')
        return modality
    
class TourneySchema(TourneyBase):
    id: Optional[int]
    
    status_id: int
    created_by: str
    created_date: datetime = datetime.today()
    updated_by: str
    updated_date: datetime = datetime.today()
    
    class Config:
        orm_mode = True
        
class TourneyCreated(BaseModel):
    name_tourney: Optional[str]
    id_tourney: Optional[str]
    modality: Optional[str]
    summary_tourney: Optional[str]
    startDate: Optional[date]