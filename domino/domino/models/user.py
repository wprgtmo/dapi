# Routes user.py
"""coding=utf-8."""

import uuid

from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, DateTime
from ..config.db import Base


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
    
    # datos para el perfil de usuarios
    sex = Column(String(1), nullable=True)
    birthdate = Column(Date, nullable=True)
    alias = Column(String(30), nullable=True)
    job = Column(String(120), nullable=True)
    city_id = Column(Integer, ForeignKey("resources.city.id"), nullable=True, comment="City to which the player belongs")
    photo = Column(String(255), nullable=True)
    
    #datos del ranking
    elo = Column(Integer, nullable=True)
    ranking = Column(String(2), nullable=True)
    
    receive_notifications = Column(Boolean, nullable=False, default=False)
     
    def dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "is_active": self.is_active,
            "country_id": self.country_id,
            "sex": self.sex,
            "birthdate": self.birthdate,
            "alias": self.alias,
            "job": self.job,
            "photo": self.photo,
            "city_id": self.city_id
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


class UserEventRoles(Base):
    """UserEventRoles Class contains standard information for Roles of User"""
 
    __tablename__ = "user_eventroles"
    __table_args__ = {'schema' : 'enterprise'}
    
    username = Column(String(50), primary_key=True)
    eventrol_id = Column(Integer, ForeignKey("resources.event_roles.id"), primary_key=True)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    
    def dict(self):
        return {
            "username": self.username,
            "user_follow": self.user_follow,
            "created_date": self.created_date,
            "is_active": self.is_active
        }