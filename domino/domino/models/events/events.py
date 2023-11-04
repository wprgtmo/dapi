# Routes user.py
"""coding=utf-8."""

import uuid
from datetime import date
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, Text, Float
from ...config.db import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())

class Event(Base):
    """Event Class contains standard information for a Event."""
 
    __tablename__ = "events"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    close_date = Column(Date, nullable=False)
    registration_date  = Column(Date, nullable=False)
    registration_price  = Column(Float, nullable=True)
    city_id = Column(Integer, ForeignKey("resources.city.id"), nullable=False)
    main_location = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    image = Column(Text, nullable=True)
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)  # perfil que lo creo
    
    tourney = relationship("Tourney")
    # tourneys = relationship("Tourney", back_populates="event")
    
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date,
            "close_date": self.close_date,
            "city_id": self.city_id,
            "main_location": self.main_location,
            "summary": self.comments,
            "image": self.image,
            "status_id": self.status,
            "photo": self.photo,
            "profile_id": self.profile_id
        }


class EventsFollowers(Base):
    """ProfileFollowers Class contains standard information for a Profile of Followers."""
 
    # puede estar siguinedo un evento, un torneo, una ronda, un jugador.....
    __tablename__ = "events_followers"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), unique=True)
    username = Column(String, nullable=False)
    element_type = Column(String(30), nullable=False)
    element_id = Column(String, unique=False)
    created_by = Column(String, nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    
    is_active = Column(Boolean, nullable=False, default=False)
    
    def dict(self):
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "username": self.username,
            "element_type": self.element_type,
            "element_id": self.element_id,
            "created_date": self.created_date,
            "is_active": self.is_active
        }
        