"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# from domino.schemas.ciudad import CiudadSchema
   
class PaisBase(BaseModel):
    nombre: str
   
class PaisSchema(PaisBase):
    id: Optional[int]
    is_active: bool = True
    # ciudades: List[CiudadSchema] = []
     
    class Config:
        orm_mode = True
      