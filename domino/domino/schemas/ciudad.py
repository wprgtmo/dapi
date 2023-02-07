"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel

class CiudadBase(BaseModel):
    nombre: str
    
class CiudadCreate(CiudadBase):
    pais_id: int
    
class CiudadSchema(CiudadCreate):
    id: int
     
    class Config:
        orm_mode = True
                
class CiudadInfo(object):
    pass 
