"""coding=utf-8."""

import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, Text, Float, DateTime
from ..config.db import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())

class Post(Base):
    """Post Class contains standard information for a Post."""
 
    __tablename__ = "post"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    summary = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.now())
    is_active = Column(Boolean, nullable=False, default=True)
    allow_comment = Column(Boolean, nullable=False, default=True)
    show_count_like = Column(Boolean, nullable=False, default=True)
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)  # perfil que lo creo
    
    files = relationship("PostFiles")
    
    def dict(self):
        return {
            "id": self.id,
            "summary": self.summary,
            'created_by': self.created_by,
            "is_active": self.is_active,
            "allow_comment": self.allow_comment,
            "show_count_like": self.show_count_like,
            "profile_id": self.profile_id
            }

class PostFiles(Base):
    """PostFiles Class contains standard information for files asociate at Post."""
 
    __tablename__ = "post_files"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    post_id = Column(String, ForeignKey("post.post.id"), nullable=False)
    path = Column(Text, nullable=False)
    
    def dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "path": self.path,
            }                
class PostLikes(Base):
    """PostLikes Class contains standard information for likes of Post."""
 
    __tablename__ = "post_likes"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    post_id = Column(String, ForeignKey("post.post.id"), nullable=False)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)  # perfil que lo creo
    
    def dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "created_by": self.created_by,
            "created_date": self.created_date,
            "profile_id": self.profile_id
        }
        
class PostComments(Base):
    """PostComments Class contains standard information for Comments of Post."""
 
    __tablename__ = "post_comments"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    post_id = Column(String, ForeignKey("post.post.id"), nullable=False)
    summary = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)  # perfil que lo creo
    
    def dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            'summary': self.summary,
            "profile_id": self.profile_id,
            "created_by": self.created_by,
            "created_date": self.created_date,
            "profile_id": self.profile_id
        }
   
class CommentLikes(Base):
    """CommentLikes Class contains standard information for likes of Comments"""
 
    __tablename__ = "comment_likes"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    comment_id = Column(String, ForeignKey("post.post_comments.id"), nullable=False)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)  # perfil que lo creo
    
    def dict(self):
        return {
            "id": self.id,
            "comment_id": self.comment_id,
            "created_by": self.created_by,
            "created_date": self.created_date,
            "profile_id": self.profile_id
        }
        
class CommentComments(Base):
    """CommentComments Class contains standard information for Comments of Comment."""
 
    __tablename__ = "comment_comments"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    comment_id = Column(String, ForeignKey("post.post_comments.id"), nullable=False)
    summary = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)  # perfil que lo creo
    
    def dict(self):
        return {
            "id": self.id,
            "comment_id": self.comment_id,
            'summary': self.summary,
            "created_by": self.created_by,
            "created_date": self.created_date,
            "profile_id": self.profile_id
        }
               