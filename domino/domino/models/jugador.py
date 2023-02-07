"""coding=utf-8."""

from email.policy import default
from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean
from ..config.db import Base

# class Jugador(Base):
#     """Clase Jugador. Gestionar todas las funcionalidades para jugadores."""
 
#     __tablename__ = "jugador"
#     __table_args__ = {'schema' : 'eventos'}
     
#     id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
#     nombre = Column(String(120), nullable=False)
#     telefono = Column(String(15), nullable=True)
#     sexo = Column(String(1), nullable=True)
#     foto = Column(String(255), nullable=True)
#     correo = Column(String(120), nullable=True)
#     nro_identidad = Column(String(30), nullable=False)
#     alias = Column(String(30), nullable=True)
#     fecha_nacimiento = Column(Date, nullable=True)
#     ocupacion = Column(String(120), nullable=True)
#     comentario = Column(String(255), nullable=True)
#     nivel = Column(String(30), nullable=True)
#     elo = Column(Integer, nullable=True)
#     ranking = Column(String(2), nullable=True)
#     tipo = Column(String(1), nullable=True)
#     ciudad_id = Column(Integer, ForeignKey("configuracion.ciudad.id"), comment="Ciudad a que pertenece el jugador")
#     is_active = Column(Boolean, nullable=False, default=True)
#     # ciudad = relationship("Ciudad", back_populates="jugadores")
        
#     def dict(self):
#         return {
#             "id": self.id,
#             "nombre": self.nombre,
#             "telefono": self.telefono,
#             "sexo": self.sexo,
#             "foto": self.foto,
#             "correo": self.correo,
#             "nro_identidad": self.nro_identidad,
#             "alias": self.alias,
#             "fecha_nacimiento": self.fecha_nacimiento,
#             "ocupacion": self.ocupacion,
#             "comentario": self.comentario,
#             "nivel": self.nivel,
#             "elo": self.elo,
#             "ranking": self.ranking,
#             "tipo": self.tipo,
#             "ciudad_id": self.ciudad_id,
#             "is_active": self.is_active
#             # "ciudad": self.ciudad.nombre
#         }
