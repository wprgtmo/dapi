"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class ProfileTypeBase(BaseModel):
    name: str
    description: str
   
class ProfileTypeSchema(ProfileTypeBase):
    id: Optional[int]
    created_date: datetime = datetime.now()
    created_by: str = 'foo'
     
    class Config:
        orm_mode = True