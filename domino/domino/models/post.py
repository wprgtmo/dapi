"""coding=utf-8."""

import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, Text, Float, DateTime
from ..config.db import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())

class PostType(Base):
    """PostType Class contains standard information for a Post Type."""
 
    __tablename__ = "post_type"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(100), nullable=False)
    created_by = Column(String(50), nullable=False, default='foo')
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "created_date": self.created_date
        }

class Post(Base):
    """Post Class contains standard information for a Post."""
 
    __tablename__ = "post"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    post_type = Column(String(100), ForeignKey("post.post_type.name"), nullable=False)
    entity_id = Column(String, nullable=True)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    publication_date = Column(Date, nullable=False, default=datetime.today())
    expire_date = Column(Date, nullable=True)
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=True)
    updated_date = Column(Date, nullable=False, default=datetime.today())
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    
    images = relationship("PostImages")
    # images = relationship("PostImages", back_populates="post")
    
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "image": self.image,
            "post_type": self.post_type,
            "entity_id": self.entity_id,
            "publication_date": self.publication_date,
            "expire_date": self.expite_date,
            "status_id": self.status_id
        }

class PostImages(Base):
    """PostImages Class contains standard information for images of Post."""
 
    __tablename__ = "post_images"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    post_id = Column(String, ForeignKey("post.post.id"), nullable=False)
    image = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    
    def dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "image": self.image,
            "created_by": self.created_by,
            "created_date": self.created_date
        }                
class PostLikes(Base):
    """PostLikes Class contains standard information for likes of Post."""
 
    __tablename__ = "post_likes"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    post_id = Column(String, ForeignKey("post.post.id"), nullable=False)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    
    def dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "created_by": self.created_by,
            "created_date": self.created_date
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
    
    def dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            'summary': self.summary,
            "created_by": self.created_by,
            "created_date": self.created_date
        }

class PostShares(Base):
    """PostShares Class contains standard information for Shares of Post."""
 
    __tablename__ = "post_shares"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    post_id = Column(String, ForeignKey("post.post.id"), nullable=False)
    summary = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    
    def dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            'summary': self.summary,
            "created_by": self.created_by,
            "created_date": self.created_date
        }
        
class PostSharesUsers(Base):
    """PostSharesUsers Class contains standard information for Shares of Post."""
 
    __tablename__ = "post_shares_users"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    share_id = Column(String, ForeignKey("post.post_shares.id"), nullable=False)
    user_name = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    
    def dict(self):
        return {
            "id": self.id,
            "share_id": self.share_id,
            'user_name': self.user_name
        }