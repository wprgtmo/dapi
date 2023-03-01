# Routes user.py
"""coding=utf-8."""

import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, Text, Float
from ..config.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class Tourney(Base):
    """Tourney Class contains standard information for a Tourney."""
 
    __tablename__ = "tourney"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, ForeignKey("events.events.id"), nullable=False)
    modality = Column(String(30), nullable=False)
    name = Column(String(100), nullable=True)
    comments = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    close_date = Column(Date, nullable=False)
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    image = Column(String(100), nullable=True)
    manage_id = Column(String, ForeignKey("enterprise.users.id"), nullable=False)
    players_number = Column(Integer, default=4)  # jugadores guardar para las estadísticas
    referees_number = Column(Integer, default=0)  # arbitros
    tables_number = Column(Integer, default=0)
    round_number = Column(Integer, default=0)
    created_by = Column(String, ForeignKey("enterprise.users.id"), nullable=False)
    created_date = Column(Date, nullable=False)
    updated_date = Column(Date, nullable=False)
    updated_by = Column(String, ForeignKey("enterprise.users.id"), nullable=False)
    
    def dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "modality": self.modality,
            "name": self.name,
            "comments": self.comments,
            "start_date": self.start_date,
            "close_date": self.close_date,
            "status_id": self.status_id,
            "image": self.image,
            "image": self.birthdate,
            "manage_id": self.manage_id
        }
    
class Players(Base):
    """Players Class contains standard information for a Players of Tourney."""

    __tablename__ = "players"
    __table_args__ = {'schema' : 'events'}
    
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False, primary_key=True)
    user_id = Column(String, ForeignKey("enterprise.users.id"), nullable=False, primary_key=True)
    nivel = Column(String(50), nullable=True)  # nivel del jugador en ese torneo
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "user_id": self.user_id,
            "nivel": self.nivel
        }
        
class Referees(Base):
    """Referees Class contains standard information for a Referees of Tourney."""

    __tablename__ = "referees"
    __table_args__ = {'schema' : 'events'}
    
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False, primary_key=True)
    user_id = Column(String, ForeignKey("enterprise.users.id"), nullable=False, primary_key=True)
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "user_id": self.user_id
        }
        
class Sponsors(Base):
    """Sponsors Class contains standard information for a Sponsors of Tourney.""" # patrocinadores

    __tablename__ = "sponsors"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(Integer, primary_key=True)
    tourney_id = Column(String, ForeignKey("events.tourney.id"))
    name = Column(Text, nullable=False)
    
    def dict(self):
        return {
            "id": self.id,
            "tourney_id": self.tourney_id,
            "name": self.name
        }
        
class GameRules(Base):
    """Game rules Class contains standard information for game rules of Tourney.""" 

    __tablename__ = "gamerules"
    __table_args__ = {'schema' : 'events'}
    
    tourney_id = Column(String, ForeignKey("events.tourney.id"), primary_key=True)
    amount_points = Column(Integer, nullable=True, default=100)
    amount_time = Column(Integer, nullable=True, default=60)
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "amount_points": self.amount_points,
            "amount_time": self.amount_time
        }
        
class Pairs(Base):
    """Pairs Class contains standard information for Pairs of domino of Tourney.""" 

    __tablename__ = "pairs"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"))
    one_player = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    two_player = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    name = Column(String(100), nullable=True)
    
    
    event_id = Column(String, ForeignKey("events.events.id"), nullable=False)
    modality = Column(String(30), nullable=False)
    
    
    
    amount_points = Column(Integer, nullable=True, default=100)
    amount_time = Column(Integer, nullable=True, default=60)
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "amount_points": self.amount_points,
            "amount_time": self.amount_time
        }