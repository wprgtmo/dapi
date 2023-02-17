"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel

class CityBase(BaseModel):
    name: str
    
class CityCreate(CityBase):
    country_id: int
    
class CitySchema(CityCreate):
    id: int
     
    class Config:
        orm_mode = True
                
class CityInfo(object):
    pass 
