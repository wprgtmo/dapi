"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List

class PostBase(BaseModel):
    summary: Optional[str]
    allow_comment: Optional[bool]
    show_count_like: Optional[bool]
    # files: List[str]
   
    @validator('summary')
    def summary_not_empty(cls, summary):
        if not summary:
            raise ValueError('Comentario de Post Requerido')
        return summary
    
class PostSchema(PostBase):
    id: Optional[int]
    
    created_by: str
    created_date: datetime = datetime.now()
    updated_by: str
    updated_date: datetime = datetime.today()
    is_active: bool = True
    class Config:
        orm_mode = True

class PostUpdated(BaseModel):
    summary: Optional[str]
    allow_comment: Optional[bool]
    show_count_like: Optional[bool]
    
    @validator('summary')
    def summary_not_empty(cls, summary):
        if not summary:
            raise ValueError('Comentario de Post Requerido')
        return summary