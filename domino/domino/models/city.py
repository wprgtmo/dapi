"""coding=utf-8."""

from email.policy import default
from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean
from ..config.db import Base

class City(Base):
    """Class City. Manage all functionalities for cities."""
 
    __tablename__ = "city"
    __table_args__ = {'schema' : 'resources'}
     
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    country_id = Column(Integer, ForeignKey("resources.country.id"))
    is_active = Column(Boolean, nullable=False, default=True)
        
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "country_id": self.country_id, 
            "is_active": self.is_active,
            "country": self.country.nombre
            
        }