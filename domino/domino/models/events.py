# Routes user.py
"""coding=utf-8."""

import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, Text, Float
from ..config.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class Event(Base):
    """Event Class contains standard information for a Event."""
 
    __tablename__ = "events"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    package_id = Column(Integer, ForeignKey("resources.packages.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    close_date = Column(Date, nullable=False)
    registration_date  = Column(Date, nullable=False)
    registration_price  = Column(Float, nullable=True)
    city_id = Column(Integer, ForeignKey("resources.city.id"), nullable=False)
    main_location = Column(String(255), nullable=True)
    comments = Column(Text, nullable=True)
    image = Column(String(100), nullable=True)
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    created_by = Column(String, ForeignKey("enterprise.users.id"), nullable=False)
    created_date = Column(Date, nullable=False)
    updated_by = Column(String, ForeignKey("enterprise.users.id"), nullable=False)
    updated_date = Column(Date, nullable=False)
    
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "package_id": self.package_id,
            "start_date": self.start_date,
            "close_date": self.close_date,
            "registration_date": self.registration_date,
            "registration_price": self.registration_price,
            "city_id": self.city_id,
            "main_location": self.main_location,
            "comments": self.comments,
            "image": self.image,
            "status_id": self.status,
            "photo": self.photo,
            "city_id": self.city_id
        }
