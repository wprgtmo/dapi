# Routes userprofile.py
"""coding=utf-8."""

import uuid

from datetime import datetime, date
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, DateTime
from ..config.db import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())


class MemberProfile(Base):
    """MemberProfile Class contains standard information for a Profile of User."""
 
    __tablename__ = "member_profile"
    __table_args__ = {'schema' : 'enterprise'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(300), nullable=False)
    email = Column(String(50), nullable=False)
    rolevent_name = Column(String, ForeignKey("resources.event_roles.name"), nullable=False) # Individual/Parejas/Equipo/Arbitro
    city_id = Column(Integer, ForeignKey("resources.city.id"), nullable=True, comment="City to which the player belongs")
    photo = Column(String(255), nullable=True)
    
    #datos del ranking
    elo = Column(Integer, nullable=True)
    ranking = Column(String(2), nullable=True)
    
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    is_ready = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    users_member = relationship("MemberUsers")
     
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "photo": self.photo,
            "city_id": self.city_id
        }
        
        
class MemberUsers(Base):
    """MemberUsers Class contains standard information for a Profile of User."""
 
    __tablename__ = "member_users"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.member_profile.id"), primary_key=True)
    username = Column(String, ForeignKey("enterprise.users.username"), primary_key=True)
    is_principal = Column(Boolean, nullable=False, default=False)
    
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
     
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "photo": self.photo,
            "city_id": self.city_id
        }
