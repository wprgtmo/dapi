# Routes exampledate.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.services.enterprise.exampledata import insert_user_examples, insert_others_profiles, create_events, \
    create_tourneys, created_invitations_tourneys, accepted_invitations_tourneys, created_players, update_elo
  
exampledata_route = APIRouter(
    tags=["ExampleData"],
    # dependencies=[Depends(JWTBearer())]   
)

@exampledata_route.post("/exampledata/step_1_users", summary="Crate generic users")
def insert_data(request:Request, db: Session = Depends(get_db)):
    return insert_user_examples(request, db=db)

@exampledata_route.post("/exampledata/step_2_profiles", summary="Crate Others profiles")
def insert_profile_data(request:Request, db: Session = Depends(get_db)):
    return insert_others_profiles(request, db=db)

@exampledata_route.post("/exampledata/step_2a_profiles", summary="Update Elo at player")
def update_elo_data(request:Request, db: Session = Depends(get_db)):
    return update_elo(request, db=db)

@exampledata_route.post("/exampledata/step_3_events", summary="Create Events")
def insert_event_data(request:Request, username: str, db: Session = Depends(get_db)):
    return create_events(request, username, db=db)

@exampledata_route.post("/exampledata/step_4_tourneys", summary="Create two Tourneys")
def insert_tourney_data(request:Request, db: Session = Depends(get_db)):
    return create_tourneys(request, db=db)

@exampledata_route.post("/exampledata/step_5_invitations", summary="Create invitations for Tourneys")
def insert_invitations_tourney_data(request:Request, db: Session = Depends(get_db)):
    return created_invitations_tourneys(request, db=db)

@exampledata_route.post("/exampledata/step_6_invitations", summary="Acepted invitations for Tourneys")
def acepted_invitations_tourney_data(request:Request, db: Session = Depends(get_db)):
    return accepted_invitations_tourneys(request, db=db)

@exampledata_route.post("/exampledata/step_7_players", summary="Created Players")
def insert_players_data(request:Request, db: Session = Depends(get_db)):
    return created_players(request, db=db)
