"""coding=utf-8."""

from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean, Float
from ..config.db import Base

class Packages(Base):
    """Class Packages. Manage all the functionalities for the packages to be marketed."""
 
    __tablename__ = "packages"
    __table_args__ = {'schema' : 'resources'}
     
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    type = Column(String(60), nullable=False)    #individual, pareja, equipo
    players_number = Column(Integer, default=4)
    price = Column(Float, default=0.00)
    is_active = Column(Boolean, nullable=False, default=True)
        
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "players_number": self.players_number,
            "price": self.price,
            "is_active": self.is_active
        }
