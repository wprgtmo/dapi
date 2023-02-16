"""coding=utf-8."""
from typing import Optional, Any
 
from pydantic import BaseModel
   
class ResultObject(BaseModel):
    sucess: bool = True
    status_code: str = '200'
    detail: str = 'Operación satisfactoria'
    data: Any
    
class ResultData(ResultObject):
    page: Optional[int] = 1
    per_page: Optional[int] = 6
    total: Optional[int] = 0
    total_pages: Optional[int] = 0