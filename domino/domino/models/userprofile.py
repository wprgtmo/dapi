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

class ProfileType(Base):
    """ProfileType Class contains standard information for all Profile Type."""
 
    __tablename__ = "profile_type"
    __table_args__ = {'schema' : 'enterprise'}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(150), nullable=False)
    created_by = Column(String(50), nullable=False, default='foo')
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    
    by_default = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "created_date": self.created_date,
            "by_default": self.by_default,
            "is_active": self.is_active
        }
        
class ProfileMember(Base):
    """ProfileMember Class contains standard information for a Profile of User."""
 
    __tablename__ = "profile_member"
    __table_args__ = {'schema' : 'enterprise'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    profile_type = Column(String, ForeignKey("enterprise.profile_type.name"), nullable=False) # Jugador/Arbitro
    name = Column(String(300), nullable=False)
    email = Column(String(300), nullable=True)
    photo = Column(String(255), nullable=True)
    city_id = Column(Integer, ForeignKey("resources.city.id"), nullable=True, comment="City to which the player belongs")
    
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    receive_notifications = Column(Boolean, nullable=False, default=False)
    is_ready = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    profile_users = relationship("ProfileUsers")
    profile_single_player = relationship("SingleProfile")
    profile_default_user = relationship("DefaultUserProfile")
    profile_referee_player = relationship("RefereeProfile")
    profile_pair_player = relationship("PairProfile")
    profile_team_player = relationship("TeamProfile")
     
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "photo": self.photo,
            "city_id": self.city_id
        }
        
class ProfileUsers(Base):
    """ProfileUsers Class contains standard information for a Profile of User."""
 
    __tablename__ = "profile_users"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    username = Column(String, ForeignKey("enterprise.users.username"), primary_key=True)
    is_principal = Column(Boolean, nullable=False, default=False)
    
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    
    is_confirmed = Column(Boolean, nullable=False, default=False)
    
    def dict(self):
        return {
            "profile_id": self.profile_id,
            "username": self.username,
            "is_principal": self.is_principal,
            "is_confirmed": self.is_confirmed
        }
class SingleProfile(Base):
    """SingleProfile Class contains standard information for a Profile of Single Player"""
 
    __tablename__ = "profile_single_player"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    elo = Column(Integer, nullable=True)
    ranking = Column(String(2), nullable=True)
    
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
     
    def dict(self):
        return {
            "profile_id": self.profile_id,
            "elo": self.elo,
            "ranking": self.ranking
        }
        
class DefaultUserProfile(Base):
    """DefaultUserProfile Class contains standard information for a Profile of Default User"""
 
    __tablename__ = "profile_default_user"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    
    sex = Column(String(1), nullable=True)
    birthdate = Column(Date, nullable=True)
    alias = Column(String(30), nullable=True)
    job = Column(String(120), nullable=True)
    city_id = Column(Integer, ForeignKey("resources.city.id"), nullable=True, comment="City to which the player belongs")
    
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
     
    def dict(self):
        return {
            "profile_id": self.profile_id,
            "sex": self.sex,
            "birthdate": self.birthdate,
            "alias": self.alias,
            "job": self.job
            }

class RefereeProfile(Base):
    """RefereeProfile Class contains standard information for a Profile of Referee"""
 
    __tablename__ = "profile_referee"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    
    level = Column(String(60), nullable=True)
    
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
     
    def dict(self):
        return {
            "profile_id": self.profile_id,
            "level": self.level   # alcance Internacional, Regional
        }

class PairProfile(Base):
    """PairProfile Class contains standard information for a Profile of Pair"""
 
    __tablename__ = "profile_pair_player"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    
    level = Column(String(60), nullable=True)
    
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
     
    def dict(self):
        return {
            "profile_id": self.profile_id,
            "level": self.level   # alcance Internacional, Regional
        }

class TeamProfile(Base):
    """TeamProfile Class contains standard information for a Profile of Team"""
 
    __tablename__ = "profile_team_player"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    
    level = Column(String(60), nullable=True)
    amount_members = Column(Integer, default=4)
    
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
     
    def dict(self):
        return {
            "profile_id": self.profile_id,
            "level": self.level,   # alcance Internacional, Regional
            "amount_members": self.amount_members
        }