"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List

class PostBase(BaseModel):
    title: str
    summary: Optional[str]
    image: Optional[str]
    entity_type: Optional[str]
    entity_id: Optional[str]
    publication_date: Optional[datetime] = datetime.today()
    expite_date: Optional[datetime] = datetime.today()
   
    @validator('title')
    def title_not_empty(cls, title):
        if not title:
            raise ValueError('Título de Post Requerido')
        return title
    
class PostSchema(PostBase):
    id: Optional[int]
    
    status_id: int
    created_by: str
    created_date: datetime = datetime.today()
    updated_by: str
    updated_date: datetime = datetime.today()
    
    class Config:
        orm_mode = True
        
