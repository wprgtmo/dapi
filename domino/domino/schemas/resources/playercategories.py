"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

   
class EventLevelsBase(BaseModel):
    level: str
    description: str
    value: float
    
    class Config:
        orm_mode = True
    
class EventScopesBase(BaseModel):
    scope: str
    description: str
    value: float
    
    class Config:
        orm_mode = True
        
class PlayerCategoriesBase(BaseModel):
    name: str
    value_k: float
    begin_elo: float
    end_elo: float
    width: float
    scope: int
    
    class Config:
        orm_mode = True