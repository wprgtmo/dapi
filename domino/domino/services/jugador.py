# from unicodedata import name
# from fastapi import HTTPException
# from domino.models.jugador import Jugador
# from domino.schemas.jugador import JugadorBase, JugadorSchema, JugadorInfo
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError, IntegrityError
# from passlib.context import CryptContext
# from domino.auth_bearer import decodeJWT
# from typing import Dict, List
            
# def get_all(request: List[JugadorInfo], skip: int, limit: int, db: Session):  
#     data = db.query(Jugador).offset(skip).limit(limit).all()   
#     lst_data = []
#     for item in data: 
#         lst_data.append(create_row_jugador(item))
#     return lst_data

# def create_row_jugador(item):
#     one_jugador = JugadorInfo()
#     one_jugador.id = item.id
#     one_jugador.nombre = item.nombre
#     one_jugador.telefono = item.telefono
#     one_jugador.sexo = item.sexo
#     one_jugador.foto = item.foto
#     one_jugador.correo = item.correo
#     one_jugador.nro_identidad = item.nro_identidad
#     one_jugador.alias = item.alias
#     one_jugador.fecha_nacimiento = item.fecha_nacimiento
#     one_jugador.ocupacion = item.ocupacion
#     one_jugador.comentario = item.comentario
#     one_jugador.nivel = item.nivel
#     one_jugador.elo = item.elo
#     one_jugador.ranking = item.ranking
#     one_jugador.tipo = item.tipo
#     one_jugador.ciudad_id = item.ciudad_id
#     one_jugador.ciudad = item.ciudad.nombre
#     return one_jugador

# def new(db: Session, jugador: JugadorSchema):
    
#     db_jugador = Jugador(nombre=jugador.nombre, telefono=jugador.telefono, sexo=jugador.sexo,
#                          foto=jugador.foto, correo=jugador.correo, nro_identidad=jugador.nro_identidad,
#                          alias=jugador.alias, fecha_nacimiento=jugador.fecha_nacimiento, ocupacion=jugador.ocupacion,
#                          comentario=jugador.comentario, nivel=jugador.nivel, elo=jugador.elo,
#                          ranking=jugador.ranking, tipo=jugador.tipo, ciudad_id=jugador.ciudad_id)
    
#     try:
#         db.add(db_jugador)
#         db.commit()
#         db.refresh(db_jugador)
#         return db_jugador
#     except (Exception, SQLAlchemyError, IntegrityError) as e:
#         print(e)
#         msg = 'Ha ocurrido un error al crear al jugador'               
#         raise HTTPException(status_code=403, detail=msg)
    
# def get_one(jugador_id: str, db: Session):  
#     return db.query(Jugador).filter(Jugador.id == jugador_id).first()

# def delete(jugador_id: str, db: Session):
#     try:
#         db_jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
#         db.delete(db_jugador)
#         db.commit()
#         return True
#     except (Exception, SQLAlchemyError) as e:
#         print(e)
#         raise HTTPException(status_code=404, detail="No es posible eliminar")
    
# def update(jugador_id: str, jugador: JugadorSchema, db: Session):
       
#     db_jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    
#     if db_jugador:
#         db_jugador.nombre = jugador.nombre
#         db_jugador.telefono = jugador.telefono
#         db_jugador.sexo = jugador.sexo
#         db_jugador.foto = jugador.foto
#         db_jugador.correo = jugador.correo
#         db_jugador.nro_identidad = jugador.nro_identidad
#         db_jugador.fecha_nacimiento = jugador.fecha_nacimiento
#         db_jugador.ocupacion = jugador.ocupacion
#         db_jugador.comentario = jugador.comentario
#         db_jugador.nivel = jugador.nivel
#         db_jugador.elo = jugador.elo
#         db_jugador.ranking = jugador.ranking
#         db_jugador.tipo = jugador.tipo
#         db_jugador.ciudad_id = jugador.ciudad_id
                         
#         try:
#             db.add(db_jugador)
#             db.commit()
#             db.refresh(db_jugador)
#             return db_jugador
#         except (Exception, SQLAlchemyError) as e:
#             print(e.code)
#             if e.code == "gkpj":
#                 raise HTTPException(status_code=400, detail="Ya existe un jugador con esos datos")
#     else:
#         raise HTTPException(status_code=400, detail="No existe jugadorad con ese ID")
