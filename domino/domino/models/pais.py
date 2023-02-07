"""coding=utf-8."""

from email.policy import default
from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean
from ..config.db import Base

class Pais(Base):
    """Clase Pais. Gestionar todas las funcionalidades para paises."""
 
    __tablename__ = "pais"
    __table_args__ = {'schema' : 'configuracion'}
     
    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # ciudades = relationship("Ciudad", back_populates="pais")
        
    def dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "is_active": self.is_active
        }
