"""coding=utf-8."""

import uuid
from datetime import date
from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean, Text, DateTime, Float
from ...config.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class DominoCategory(Base):
    """DominoCategory Class contains standard information for  Domino categories at Torney."""
 
    __tablename__ = "domino_categories"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False)
    category_number = Column(String(100), nullable=False)
    position_number = Column(Integer, nullable=False)
    elo_min = Column(Float, nullable=False)
    elo_max = Column(Float, nullable=False)
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "category_number": self.category_number,
            "position_number": self.position_number,
            "elo_min": self.elo_min,
            "elo_max": self.elo_max
            }

