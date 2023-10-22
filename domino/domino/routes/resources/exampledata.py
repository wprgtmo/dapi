# Routes exampledate.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.services.enterprise.exampledata import insert_user_examples, insert_others_profiles, create_events, \
    create_tourneys, created_invitations_tourneys, accepted_invitations_tourneys, created_players, update_elo, \
    clear_all_bd
  
from domino.services.events.domino_round import configure_rounds
from domino.services.events.domino_boletus import created_boletus_for_round

exampledata_route = APIRouter(
    tags=["ExampleData"],
    # dependencies=[Depends(JWTBearer())]   
)

@exampledata_route.post("/exampledata/step_1_clear_bd", summary="Clears BD")
def insert_data(request:Request, db: Session = Depends(get_db)):
    return clear_all_bd(request, db=db)

@exampledata_route.post("/exampledata/step_2_users", summary="Create generic users")
def insert_data(request:Request, db: Session = Depends(get_db)):
    return insert_user_examples(request, db=db)

@exampledata_route.post("/exampledata/step_3_profiles", summary="Create Others profiles")
def insert_profile_data(request:Request, db: Session = Depends(get_db)):
    return insert_others_profiles(request, db=db)

@exampledata_route.post("/exampledata/step_4a_profiles", summary="Update Elo at player")
def update_elo_data(request:Request, db: Session = Depends(get_db)):
    return update_elo(request, db=db)

@exampledata_route.post("/exampledata/step_5_events", summary="Create Events")
def insert_event_data(request:Request, username: str, db: Session = Depends(get_db)):
    return create_events(request, username, db=db)

@exampledata_route.post("/exampledata/step_6_tourneys", summary="Create two Tourneys")
def insert_tourney_data(request:Request, db: Session = Depends(get_db)):
    return create_tourneys(request, db=db)

@exampledata_route.post("/exampledata/step_7_invitations", summary="Create invitations for Tourneys")
def insert_invitations_tourney_data(request:Request, db: Session = Depends(get_db)):
    return created_invitations_tourneys(request, db=db)

@exampledata_route.post("/exampledata/step_8_invitations", summary="Acepted invitations for Tourneys")
def acepted_invitations_tourney_data(request:Request, db: Session = Depends(get_db)):
    return accepted_invitations_tourneys(request, db=db)

@exampledata_route.post("/exampledata/step_9_players", summary="Created Players")
def insert_players_data(request:Request, db: Session = Depends(get_db)):
    return created_players(request, db=db)

@exampledata_route.post("/exampledata/step_10_scale", summary="Crear Parejas por Rondas a partir del sorteo")
def configure_pairs_rounds(request:Request, tourney_id:str, round_id:str, db: Session = Depends(get_db)):
    return configure_rounds(request, tourney_id=tourney_id, round_id=round_id, db=db)

@exampledata_route.post("/exampledata/step_11_players", summary="Crear Boletas y redsitribuir parejas por mesas")
def configure_boletus(request:Request, tourney_id:str, round_id:str, db: Session = Depends(get_db)):
    return created_boletus_for_round(tourney_id=tourney_id, round_id=round_id, db=db)