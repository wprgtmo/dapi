"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# from domino.schemas.ciudad import CiudadSchema
   
class StatusBase(BaseModel):
    name: str
    description: str
   
class StatusSchema(StatusBase):
    id: Optional[int]
    is_active: bool = True
    created_date: datetime = datetime.now()
     
    class Config:
        orm_mode = True
      