"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List

class PostImageCreate(BaseModel):
    image: str
    post_id: Optional[str]
    
class PosImageSchema(PostImageCreate):
    id: Optional[str]
    
    created_by: str
    created_date: datetime = datetime.today()
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