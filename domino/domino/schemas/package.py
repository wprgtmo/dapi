"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

 
class PackagesBase(BaseModel):
    name: str
    type: str
    players_number: int
    price: float
   
class PackagesSchema(PackagesBase):
    id: Optional[int]
    is_active: bool = True
     
    class Config:
        orm_mode = True
        
    