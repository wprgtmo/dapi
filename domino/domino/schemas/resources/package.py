"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List

 
class PackagesBase(BaseModel):
    name: str
    price: float
    number_individual_tourney: Optional[int]
    number_pairs_tourney: Optional[int]
    number_team_tourney: Optional[int]
   
    @validator('name')
    def name_not_empty(cls, name):
        if not name:
            raise ValueError('Nombre de Paquete es Requerido')
        return name
    
    @validator('price')
    def price_not_empty(cls, price):
        if price and price < 0:
            raise ValueError('Precio del Paquete es Requerido')
        return price
    
    
class PackagesSchema(PackagesBase):
    id: Optional[int]
    is_active: bool = True
    created_date: datetime = datetime.today()
    created_by: str
    
    class Config:
        orm_mode = True
        
