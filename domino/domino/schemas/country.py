"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# from domino.schemas.ciudad import CiudadSchema
   
class CountryBase(BaseModel):
    name: str
   
class CountrySchema(CountryBase):
    id: Optional[int]
    is_active: bool = True
     
    class Config:
        orm_mode = True
      