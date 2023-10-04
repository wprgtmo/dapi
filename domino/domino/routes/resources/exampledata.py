# Routes exampledate.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.services.enterprise.exampledata import insert_user_examples, insert_others_profiles, create_events
  
exampledata_route = APIRouter(
    tags=["Nomenclators"]   # tags=["Cities"],
    # dependencies=[Depends(JWTBearer())]   
)

@exampledata_route.post("/exampledata/step_1_users", summary="Crate generic users")
def insert_data(request:Request, db: Session = Depends(get_db)):
    return insert_user_examples(request, db=db)

@exampledata_route.post("/exampledata/step_2_profiles", summary="Crate Others profiles")
def insert_profile_data(request:Request, db: Session = Depends(get_db)):
    return insert_others_profiles(request, db=db)

@exampledata_route.post("/exampledata/step_3_events", summary="Create Events")
def insert_event_data(request:Request, db: Session = Depends(get_db)):
    return create_events(request, db=db)

@exampledata_route.post("/exampledata/step_4_tourneys", summary="Create two Tourneys")
def insert_tourney_data(request:Request, db: Session = Depends(get_db)):
    return create_tourney(request, db=db)
