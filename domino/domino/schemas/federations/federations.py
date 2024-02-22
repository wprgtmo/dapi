"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# from domino.schemas.ciudad import CiudadSchema
   
class FederationsBase(BaseModel):
    name: str
    city: Optional[int]
    country: Optional[int]
    logo: Optional[str]
   
class FederationsSchema(FederationsBase):
    id: Optional[int]
    is_active: bool = True
     
    class Config:
        orm_mode = True
        
class ClubsBase(BaseModel):
    name: str
    federations_id: int
    city: Optional[int]
    country: Optional[int]
    logo: Optional[str]
   
class FederationsSchema(FederationsBase):
    id: Optional[int]
    is_active: bool = True
     
    class Config:
        orm_mode = True