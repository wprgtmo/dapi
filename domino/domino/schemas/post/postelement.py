"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List

class PostFileCreate(BaseModel):
    path: str
    post_id: Optional[str]
    
class PosFileSchema(PostFileCreate):
    id: Optional[str]
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
        
class CommentCommentCreate(BaseModel):
    comment_id: str
    summary: Optional[str]
       
    @validator('comment_id')
    def comment_id_not_empty(cls, comment_id):
        if not comment_id:
            raise ValueError('ID de Comentario Requerido')
        return comment_id
    
class CommentCommentSchema(CommentCommentCreate):
    id: Optional[str]
    
    created_by: str
    created_date: datetime = datetime.today()
    class Config:
        orm_mode = True
        
        
class CommentLikeCreate(BaseModel):
    comment_id: str
       
    @validator('comment_id')
    def comment_id_not_empty(cls, comment_id):
        if not comment_id:
            raise ValueError('ID de Comentario Requerido')
        return comment_id
    
class CommentLikeSchema(CommentLikeCreate):
    id: Optional[str]
    
    created_by: str
    created_date: datetime = datetime.today()
    class Config:
        orm_mode = True