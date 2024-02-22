"""coding=utf-8."""

from email.policy import default
from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean
from ...config.db import Base

class Federations(Base):
    """Class Federations. Manage all functionalities for Federations."""
 
    __tablename__ = "federations"
    __table_args__ = {'schema' : 'federations'}
     
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    logo = Column(String, nullable=True)
    city_id = Column(Integer, ForeignKey("resources.city.id"), nullable=True)
    country_id = Column(Integer, ForeignKey("resources.country.id"), nullable=True)
    is_active = Column(Boolean)
           
    def dict(self):
        return {
            "id": self.id,
            "name": self.nombre,
            "logo": self.logo,
            'city_id': self.city_id,
            'country_id': self.country_id,
            "is_active": self.is_active
        }


class Clubs(Base):
    """Class Clubs. Manage all functionalities for Clubs."""
 
    __tablename__ = "clubs"
    __table_args__ = {'schema' : 'federations'}
     
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    logo = Column(String, nullable=True)
    federation_id = Column(Integer, ForeignKey("federations.federations.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("resources.city.id"), nullable=True)
    country_id = Column(Integer, ForeignKey("resources.country.id"), nullable=True)
    is_active = Column(Boolean)
        
    def dict(self):
        return {
            "id": self.id,
            "name": self.nombre,
            "logo": self.logo,
            'city_id': self.city_id,
            'country_id': self.country_id,
            "is_active": self.is_active
        }