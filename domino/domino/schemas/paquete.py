"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

 
class PaqueteBase(BaseModel):
    nombre: str
    tipo: str
    cantidad_jugadores: int
    precio: float
   
class PaqueteSchema(PaqueteBase):
    id: Optional[int]
    is_active: bool = True
     
    class Config:
        orm_mode = True
        
    