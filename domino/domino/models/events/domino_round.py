"""coding=utf-8."""

import uuid
from datetime import date
from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean, Text, DateTime
from ...config.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class DominoRounds(Base):
    """DominoRounds Class contains standard information for  Domino rounds at Torney."""
 
    __tablename__ = "domino_rounds"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    summary = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    close_date = Column(DateTime, nullable=False)
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=True)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    idx_number_table = UniqueConstraint('tourney_id', 'round_number')
    
    def dict(self):
        return {
            "id": self.id,
            "tourney_id": self.tourney_id,
            "round_number": self.round_number,
            "summary": self.summary,
            "start_date": self.start_date,
            "close_date": self.close_date,
            'status_id': self.status_id
            }
