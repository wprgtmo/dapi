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
    