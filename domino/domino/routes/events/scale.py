from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.events.domino_rounds import DominoManualScaleCreated, DominoAutomaticScaleCreated
from domino.schemas.resources.result_object import ResultObject

from domino.services.events.domino_scale import new_initial_automatic_round, new_initial_manual_round

dominoscale_route = APIRouter(
    tags=["Rounds"],
    dependencies=[Depends(JWTBearer())]   
)

# @dominoscale_route.get("/tourney/", response_model=Dict, summary="Obtain a list of Tourney.")
# def get_tourney(
#     request: Request,
#     page: int = 1, 
#     per_page: int = 6, 
#     criteria_key: str = "",
#     criteria_value: str = "",
#     db: Session = Depends(get_db)
# ):
#     return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@dominoscale_route.post("/domino/scale/initial/manual/", response_model=ResultObject, summary="Create Initial Scale..")
def create_initial_manual_scale(request:Request, tourney_id: str, loterry: List[DominoManualScaleCreated], db: Session = Depends(get_db)):
    return new_initial_manual_round(request=request, tourney_id=tourney_id, dominoscale=loterry, db=db)

@dominoscale_route.post("/domino/scale/initial/automatic/", response_model=ResultObject, summary="Create Initial Scale..")
def create_initial_automatic_scale(request:Request, tourney_id: str, loterry: List[DominoAutomaticScaleCreated], db: Session = Depends(get_db)):
    return new_initial_automatic_round(request=request, tourney_id=tourney_id, dominoscale=loterry, db=db)

# @dominoscale_route.post("/domino/scale/initial/", response_model=ResultObject, summary="Create Initial Scale..")
# def create_initial_scale(request:Request, tourney_id: str, loterry: List[DominoAutomaticScaleCreated], db: Session = Depends(get_db)):
#     return new_initial_automatic_round(request=request, tourney_id=tourney_id, dominoscale=loterry, db=db)


