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
    price = Column(Float, default=0.00)
    number_individual_tourney = Column(Integer, default=0)
    number_pairs_tourney = Column(Integer, default=0)
    number_team_tourney = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(String(50), nullable=False, default='foo')
    created_date = Column(Date, nullable=False, default=datetime.today())
    
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "number_individual_tourney": self.number_individual_tourney,
            "number_pairs_tourney": self.number_pairs_tourney,
            "number_team_tourney": self.number_team_tourney,
            "is_active": self.is_active
        }
