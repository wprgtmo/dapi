# """coding=utf-8."""
 
# from datetime import datetime, date
# from pydantic import BaseModel, EmailStr, ValidationError, validator
# from typing import Optional

# class JugadorBase(BaseModel):
#     nombre: str
#     telefono: Optional[str]
#     sexo: str
#     foto: Optional[str]
#     correo: Optional[EmailStr]
#     nro_identidad: str
#     alias: Optional[str]
#     fecha_nacimiento: Optional[date] = None
#     ocupacion: Optional[str]
#     comentario: Optional[str]
#     nivel: Optional[str]
#     elo: int
#     ranking: str
#     tipo: str
    
#     @validator('sexo')
#     def sexo_length(cls, sexo):
#         if len(sexo) != 1:
#             raise ValueError('La longitud del sexo es de 1 caracteres.')
#         if sexo not in ('F', 'M'):
#             raise ValueError('El sexo debe ser F o M.')
#         return sexo
     
# class JugadorSchema(JugadorBase):
#     id: int
#     ciudad_id: int
     
#     class Config:
#         orm_mode = True

# class JugadorInfo(object):
#     pass 