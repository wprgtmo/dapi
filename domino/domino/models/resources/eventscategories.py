"""coding=utf-8."""

from email.policy import default
from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, DateTime, Integer, Float
from ...config.db import Base

class EventLevels(Base):
    """EventLevels Class contains standard information for a Event Levels."""
 
    __tablename__ = "events_levels"
    __table_args__ = {'schema' : 'resources'}
    
    id = Column(Integer, primary_key=True)
    level = Column(String(50), nullable=False, unique=True)
    description = Column(String(50), nullable=False, unique=True)
    value = Column(Float, nullable=False)
    
    def dict(self):
        return {
            "id": self.id,
            "level": self.name,
            "description": self.description,
            "value": self.value
        }

class EventScopes(Base):
    """EventScopes Class contains standard information for a Event Scopes."""
 
    __tablename__ = "events_scopes"
    __table_args__ = {'schema' : 'resources'}
    
    id = Column(Integer, primary_key=True)
    scope = Column(String(50), nullable=False, unique=True)
    description = Column(String(50), nullable=False, unique=True)
    value = Column(Float, nullable=False)
    
    def dict(self):
        return {
            "id": self.id,
            "scope": self.name,
            "description": self.description,
            "value": self.value
        }
        
class PlayerCategories(Base):
    """PlayerCategories Class contains standard information for a Player Categories."""
 
    __tablename__ = "player_categories"
    __table_args__ = {'schema' : 'resources'}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    value_k = Column(Float, nullable=False)
    begin_elo = Column(Float, nullable=False)
    end_elo = Column(Float, nullable=False)
    width = Column(Float, nullable=False) #ancho
    scope = Column(Integer, ForeignKey("resources.events_scopes.id"))
    
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "value_k": self.value_k,
            "begin_elo": self.begin_elo,
            "end_elo": self.end_elo,
            "width": self.width,
            "scope": self.scope
        }