"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List
from domino.schemas.postelement import PostImageCreate

class PostTypeBase(BaseModel):
    name: str
    description: str
   
class PostTypeSchema(PostTypeBase):
    id: Optional[int]
    created_date: datetime = datetime.now()
     
    class Config:
        orm_mode = True
        
class PostBase(BaseModel):
    from ..schemas.post import PostImageCreate
    title: str
    summary: Optional[str]
    post_type: Optional[str]
    entity_id: Optional[str]
    publication_date: Optional[datetime] = datetime.today()
    expire_date: Optional[datetime] = datetime.today()
    images: List[PostImageCreate]
   
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
