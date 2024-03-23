"""coding=utf-8."""
 
from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional, List


class InscriptionsBase(BaseModel):
    tourney_id: str
    profile_id: str
    modality: str
    was_pay: bool
    way_payment = str
    import_pay: float
    
    @validator('tourney_id')
    def tourney_id_not_empty(cls, tourney_id):
        if not tourney_id:
            raise ValueError('Identificador del torneo es Requerido')
        return tourney_id
       
class InscriptionsSchema(InscriptionsBase):
    id: Optional[int]
    
    created_by: str
    created_date: datetime = datetime.today()
    updated_by: str
    updated_date: datetime = datetime.today()
    
    class Config:
        orm_mode = True
        
class InscriptionsCreated(BaseModel):
    tourney_id: str
    profile_id: str
    was_pay: bool
    payment_way: str
    
class InscriptionsUpdated(BaseModel):
    was_pay: bool
    payment_way: str
    
        