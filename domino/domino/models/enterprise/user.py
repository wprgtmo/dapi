# Routes user.py
"""coding=utf-8."""

import uuid

from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, DateTime
from ...config.db import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())

class Users(Base):
    """Users Class contains standard information for a User."""
 
    __tablename__ = "users"
    __table_args__ = {'schema' : 'enterprise'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String(50), nullable=False, unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(50), nullable=False)
    phone = Column(String(12), nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    country_id = Column(Integer, ForeignKey("resources.country.id"))
    security_code = Column(String(5), nullable=True)
    
    def dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "is_active": self.is_active,
            "country_id": self.country_id
        }


class UserFollowers(Base):
    """UserFollowers Class contains standard information for Followers of User"""
 
    __tablename__ = "user_followers"
    __table_args__ = {'schema' : 'enterprise'}
    
    username = Column(String(50), primary_key=True)
    user_follow = Column(String(50), primary_key=True)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    is_active = Column(Boolean, nullable=False, default=False)
    
    def dict(self):
        return {
            "username": self.username,
            "user_follow": self.user_follow,
            "created_date": self.created_date,
            "is_active": self.is_active
        }
