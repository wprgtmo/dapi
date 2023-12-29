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

class Referees(Base):
    """Referees Class contains standard information for a Referees of Tourney."""

    __tablename__ = "referees"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False, primary_key=True)
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)
    invitation_id = Column(String, ForeignKey("events.invitations.id"), nullable=False)
    
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "user_id": self.user_id
        }
    

