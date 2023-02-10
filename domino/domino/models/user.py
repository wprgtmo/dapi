# Routes user.py
"""coding=utf-8."""

import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer
from ..config.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class Users(Base):
    """Users Class contains standard information for a User."""
 
    __tablename__ = "users"
    __table_args__ = {'schema' : 'enterprise'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String(50), nullable=False, unique=True)
    fullname = Column(String(100), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    phone = Column(String(8), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    pais_id = Column(Integer, ForeignKey("configuracion.pais.id"), nullable=True)
     
    def dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "fullname": self.fullname,
            "email": self.email,
            "phone": self.phone,
            "password": self.password,
            "is_active": self.is_active,
            "pais_id": self.pais_id
        }
    
# Base.metadata.create_all(bind=engine)
