"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

  
class ExtTypeBase(BaseModel):
    ext_code: str
    type_file: str
   
class ExtTypeBaseSchema(ExtTypeBase):
    id: Optional[int]
    is_active: bool = True
    created_by: str = 'foo'
    created_date: datetime = datetime.now()
     
    class Config:
        orm_mode = True
