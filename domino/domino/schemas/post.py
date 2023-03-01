"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List

class PostTypeBase(BaseModel):
    name: str
    description: str
   
class PostTypeSchema(PostTypeBase):
    id: Optional[int]
    created_date: datetime = datetime.now()
     
    class Config:
        orm_mode = True
        
class PostBase(BaseModel):
    title: str
    summary: Optional[str]
    image: Optional[str]
    post_type: Optional[str]
    entity_id: Optional[str]
    publication_date: Optional[datetime] = datetime.today()
    expire_date: Optional[datetime] = datetime.today()
   
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
        
class PostLikeCreate(BaseModel):
    post_id: str
       
    @validator('post_id')
    def post_id_not_empty(cls, post_id):
        if not post_id:
            raise ValueError('ID de Post Requerido')
        return post_id
    
class PostLikeSchema(PostLikeCreate):
    id: Optional[str]
    
    created_by: str
    created_date: datetime = datetime.today()
    class Config:
        orm_mode = True


class PostCommentCreate(BaseModel):
    post_id: str
    summary: Optional[str]
       
    @validator('post_id')
    def post_id_not_empty(cls, post_id):
        if not post_id:
            raise ValueError('ID de Post Requerido')
        return post_id
    
class PostCommentSchema(PostCommentCreate):
    id: Optional[str]
    
    created_by: str
    created_date: datetime = datetime.today()
    class Config:
        orm_mode = True
        

class PostShareCreate(BaseModel):
    post_id: str
    summary: Optional[str]
    lst_users: Optional[list]
       
    @validator('post_id')
    def post_id_not_empty(cls, post_id):
        if not post_id:
            raise ValueError('ID de Post Requerido')
        return post_id
    
class PostShareSchema(PostShareCreate):
    id: Optional[str]
    
    created_by: str
    created_date: datetime = datetime.today()
    class Config:
        orm_mode = True