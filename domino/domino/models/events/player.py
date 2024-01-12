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
    ranking = Column(Integer, nullable=True)
    level = Column(String(60), nullable=True)  # nivel del jugador en ese torneo
    
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    
    games_played = Column(Integer)
    games_won = Column(Integer)
    games_lost = Column(Integer)
    points_positive = Column(Integer)
    points_negative = Column(Integer)
    points_difference = Column(Integer)
    
    score_expected = Column(Float)
    score_obtained = Column(Float)
    k_value = Column(Float)
    elo_current = Column(Float)
    elo_at_end = Column(Float)
    bonus_points = Column(Float)
    
    tourney = relationship('Tourney')
    status = relationship("StatusElement")
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "profile_id": self.profile_id,
            "nivel": self.nivel,
            "invitation_id": self.invitation_id
        }