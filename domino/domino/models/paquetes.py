"""coding=utf-8."""

from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean, Float
from ..config.db import Base

class Paquete(Base):
    """Clase Paquete. Gestionar todas las funcionalidades para los paquetes a comercializar."""
 
    __tablename__ = "paquetes"
    __table_args__ = {'schema' : 'configuracion'}
     
    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    tipo = Column(String(60), nullable=False)    #individual, pareja, equipo
    cantidad_jugadores = Column(Integer, default=4)
    precio = Column(Float, default=0.00)
    is_active = Column(Boolean, nullable=False, default=True)
        
    def dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "cantidad_jugadores": self.cantidad_jugadores,
            "precio": self.precio,
            "is_active": self.is_active
        }
