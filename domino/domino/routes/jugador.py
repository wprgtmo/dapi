# # Routes ciudad.py
# from fastapi import APIRouter, Depends, HTTPException, Request
# from domino.schemas.jugador import JugadorBase, JugadorSchema
# from sqlalchemy.orm import Session
# from domino.app import get_db
# from typing import List
# from domino.services.jugador import get_all, new, get_one, delete, update
# from starlette import status
# from domino.auth_bearer import JWTBearer
# import uuid
  
# jugador_route = APIRouter(
#     tags=["Jugadores"],
#     # dependencies=[Depends(JWTBearer())]   
# )

# @jugador_route.get("/jugador", response_model=List, summary="Obtener lista de Jugadores")
# def get_jugadores(
#     request: Request,
#     skip: int = 0, 
#     limit: int = 100, 
#     db: Session = Depends(get_db)
# ):
#     return get_all(request=request, skip=skip, limit=limit, db=db)

# @jugador_route.post("/jugador", response_model=JugadorSchema, summary="Crear un Jugador")
# def create_jugador(jugador: JugadorSchema, db: Session = Depends(get_db)):
#     return new(jugador=jugador, db=db)

# @jugador_route.get("/jugador/{id}", response_model=JugadorSchema, summary="Obtener un jugador por su ID")
# def get_jugador_by_id(id: int, db: Session = Depends(get_db)):
#     return get_one(jugador_id=id, db=db)

# @jugador_route.delete("/jugador/{id}", status_code=status.HTTP_200_OK, summary="Eliminar un Jugador por su ID")
# def delete_jugador(id: int, db: Session = Depends(get_db)):
#     is_delete = delete(jugador_id=str(id), db=db)
#     if is_delete:
#         raise HTTPException(status_code=200, detail="Jugador Eliminado")
#     else:
#         raise HTTPException(status_code=404, detail="Jugador no encontrado")

# @jugador_route.put("/jugador/{id}", response_model=JugadorSchema, summary="Actualizar un jugador por su ID")
# def update_jugador(id: int, jugador: JugadorSchema, db: Session = Depends(get_db)):
#     return update(db=db, jugador_id=str(id), jugador=jugador)
