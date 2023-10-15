"""coding=utf-8."""

import uuid
from datetime import date
from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean, Text, DateTime
from ...config.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class DominoScale(Base):
    """DominoScale Class contains standard information for  Domino Scale at Rounds."""
 
    __tablename__ = "domino_scale"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False)
    round_id = Column(String, ForeignKey("events.domino_rounds.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    position_number = Column(Integer, nullable=False)
    player_id = Column(String, ForeignKey("events.players.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    def dict(self):
        return {
            "id": self.id,
            "tourney_id": self.tourney_id,
            "round_id": self.round_id,
            "round_number": self.round_number,
            "position_number": self.position_number,
            "player_id": self.player_id,
            "is_active": self.is_active
            }