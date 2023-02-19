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
    package_id = Column(Integer, ForeignKey("resources.packages.id"), nullable=False)
    name = Column(String(100), nullable=False)
    city_id = Column(Integer, ForeignKey("resources.city.id"), nullable=False)
    comments = Column(Text, nullable=True)
    image = Column(String(100), nullable=True)
    status  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    created_date = Column(Date, nullable=False)
    created_by = Column(String, ForeignKey("enterprise.users.id"), nullable=False)
    updated_date = Column(Date, nullable=False)
    updated_by = Column(String, ForeignKey("enterprise.users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    close_date = Column(Date, nullable=False)
    registration_date  = Column(Date, nullable=False)
    registration_price  = Column(Float, nullable=True)
    created_by = Column(String, ForeignKey("enterprise.users.id"), nullable=False)
    players_number = Column(Integer, default=4)  # jugadores guardar para las estadísticas
    referees_number = Column(Integer, default=0)  # arbitros
    tables_number = Column(Integer, default=0)
    round_number = Column(Integer, default=0)
    bonus_round = Column(Integer, default=0)  # a partir de que ronda se bonifica
    manager = Column(String, ForeignKey("enterprise.users.id"), nullable=False)
   
    def dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "is_active": self.is_active,
            "country_id": self.country_id,
            "sex": self.sex,
            "birthdate": self.birthdate,
            "alias": self.alias,
            "job": self.job,
            "photo": self.photo,
            "city_id": self.city_id
        }
