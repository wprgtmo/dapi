"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class EventRolesBase(BaseModel):
    name: str
    description: str
   
class EventRolesSchema(EventRolesBase):
    id: Optional[int]
    created_date: datetime = datetime.now()
    created_by: str = 'foo'
     
    class Config:
        orm_mode = True