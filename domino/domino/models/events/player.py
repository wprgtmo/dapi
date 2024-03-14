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

class Players(Base):
    """Players Class contains standard information for a Players of Tourney."""

    __tablename__ = "players"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False)
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)
    invitation_id = Column(String, ForeignKey("events.invitations.id"), nullable=False)
    
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    elo = Column(Float, nullable=True)
    level = Column(String(60), nullable=True)  # nivel del jugador en ese torneo
    
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    
    tourney = relationship('Tourney')
    status = relationship("StatusElement")
    users = relationship('PlayersUser')
    profile_member = relationship('ProfileMember')
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "profile_id": self.profile_id,
            "nivel": self.nivel,
            "invitation_id": self.invitation_id
        }
        
class PlayersUser(Base):
    """Players User Class contains standard information for a Players of Tourney."""

    __tablename__ = "players_users"
    __table_args__ = {'schema' : 'events'}
    
    player_id = Column(String, ForeignKey("events.players.id"), nullable=False, primary_key=True)
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False, primary_key=True)
    level = Column(String(60), nullable=True)  
    category_id = Column(String(60), nullable=True)  
    category_number = Column(Integer, nullable=True)  
    
    elo = Column(Float, nullable=True)
    elo_current = Column(Float, nullable=True)
    elo_at_end = Column(Float, nullable=True)
    elo_ra = Column(Float, nullable=True)
    
    games_played = Column(Integer)
    games_won = Column(Integer)
    games_lost = Column(Integer)
    
    points_positive = Column(Integer)
    points_negative = Column(Integer)
    points_difference = Column(Integer)
    
    score_expected = Column(Float)
    score_obtained = Column(Float)
    k_value = Column(Float)
    
    penalty_yellow = Column(Integer)
    penalty_red = Column(Integer)
    penalty_total = Column(Integer)
    
    bonus_points = Column(Float)
    position_number_at_end = Column(Integer)
    
    player = relationship("Players", back_populates="users")
    
    def dict(self):
        return {
            "player_id": self.tourney_id,
            "profile_id": self.profile_id,
            "level": self.level
        }