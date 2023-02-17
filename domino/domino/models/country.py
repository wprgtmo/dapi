"""coding=utf-8."""

from email.policy import default
from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean
from ..config.db import Base

class Country(Base):
    """Class Country. Manage all functionalities for countries."""
 
    __tablename__ = "country"
    __table_args__ = {'schema' : 'resources'}
     
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
        
    def dict(self):
        return {
            "id": self.id,
            "name": self.nombre,
            "is_active": self.is_active
        }
