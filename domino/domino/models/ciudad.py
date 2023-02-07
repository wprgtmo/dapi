"""coding=utf-8."""

from email.policy import default
from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean
from ..config.db import Base

class Ciudad(Base):
    """Clase Ciudad. Gestionar todas las funcionalidades para ciudades."""
 
    __tablename__ = "ciudad"
    __table_args__ = {'schema' : 'configuracion'}
     
    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    pais_id = Column(Integer, ForeignKey("configuracion.pais.id"))
    is_active = Column(Boolean, nullable=False, default=True)
    # pais = relationship("Pais", back_populates="ciudades")
    # jugador = relationship("Jugador", back_populates="jugadores")
        
    def dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "pais_id": self.pais_id, #.nombre
            "is_active": self.is_active,
            "pais": self.pais.nombre
            
        }