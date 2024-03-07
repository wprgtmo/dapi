# Routes userprofile.py
"""coding=utf-8."""

import uuid

from datetime import datetime, date
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, DateTime, Float
from ...config.db import Base
from sqlalchemy.orm import relationship

# from ....domino.models.resources.city import City
from domino.models.resources.city import City

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
    profile_single_player = relationship("SingleProfile", )
    profile_default_user = relationship("DefaultUserProfile")
    profile_referee_player = relationship("RefereeProfile")
    profile_pair_player = relationship("PairProfile")
    profile_team_player = relationship("TeamProfile")
    profile_event_admon = relationship("EventAdmonProfile")
    profile_federated = relationship("FederatedProfile")
    
    city = relationship(City)
     
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
    
    single_profile_id = Column(String)  #, ForeignKey("enterprise.profile_member.id"))
    
    # profile = relationship("ProfileMember", foreign_keys=[profile_id])
    # single_profile = relationship("ProfileMember", foreign_keys=[single_profile_id])
    
    def dict(self):
        return {
            "profile_id": self.profile_id,
            "username": self.username,
            "is_principal": self.is_principal,
            "is_confirmed": self.is_confirmed,
            "single_profile_id": self.single_profile_id
        }
class SingleProfile(Base):
    """SingleProfile Class contains standard information for a Profile of Single Player"""
 
    __tablename__ = "profile_single_player"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    elo = Column(Float, nullable=True)
    
    level = Column(String(60), nullable=True)
    profile_user_id = Column(String(60), nullable=True)
    
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    club_id = Column(Integer, ForeignKey("federations.clubs.id"), nullable=True)
    
    profile = relationship("ProfileMember", back_populates="profile_single_player")
     
    def dict(self):
        return {
            "profile_id": self.profile_id,
            "elo": self.elo,
            "level": self.level,
            'profile_user_id': self.profile_user_id
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
    
    federation_id = Column(Integer, ForeignKey("federations.federations.id"), nullable=True)
    profile_user_id = Column(String, nullable=True)
    
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
    
    elo = Column(Float, nullable=True)
    
    level = Column(String(60), nullable=True)
    
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    club_id = Column(Integer, ForeignKey("federations.clubs.id"), nullable=True)
     
    def dict(self):
        return {
            "profile_id": self.profile_id,
            "elo": self.elo,
            "level": self.level
        }

class TeamProfile(Base):
    """TeamProfile Class contains standard information for a Profile of Team"""
 
    __tablename__ = "profile_team_player"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    
    elo = Column(Float, nullable=True)
    
    level = Column(String(60), nullable=True)
    amount_members = Column(Integer, default=4)
    
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    club_id = Column(Integer, ForeignKey("federations.clubs.id"), nullable=True)
     
    def dict(self):
        return {
            "profile_id": self.profile_id,
            "elo": self.elo,
            "level": self.level,
            "amount_members": self.amount_members
        }
       
class ProfileFollowers(Base):
    """ProfileFollowers Class contains standard information for a Profile of Followers."""
 
    __tablename__ = "profile_followers"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    username = Column(String, nullable=False)
    
    profile_follow_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    username_follow = Column(String, nullable=False)
    
    created_by = Column(String, nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    
    is_active = Column(Boolean, nullable=False, default=False)
    
    def dict(self):
        return {
            "profile_id": self.profile_id,
            "username": self.username,
            "profile_follow_id": self.profile_follow_id,
            "username_follow": self.username_follow,
            "created_date": self.created_date,
            "is_active": self.is_active
        }
        
class EventAdmonProfile(Base):
    """EventAdmonProfile Class contains standard information for a Profile of Event Admon"""
 
    __tablename__ = "profile_event_admon"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    
    federation_id = Column(Integer, ForeignKey("federations.federations.id"), nullable=True)
    profile_user_id = Column(String, nullable=True)
    
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
     
    def dict(self):
        return {
            "profile_id": self.profile_id,
            }
        
class FederatedProfile(Base):
    """FederatedProfilerofile Class contains standard information for a Profile of Federated"""
 
    __tablename__ = "profile_federated"
    __table_args__ = {'schema' : 'enterprise'}
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), primary_key=True)
    
    federation_id = Column(Integer, ForeignKey("federations.federations.id"), nullable=True)
    profile_user_id = Column(String, nullable=True)
    
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
     
    def dict(self):
        return {
            "profile_id": self.profile_id,
            }