from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.resources.result_object import ResultObject
from domino.schemas.events.domino_data import DominoDataCreated
from domino.schemas.events.domino_penalties import DominoPenaltiesCreated, DominoAbsencesCreated, DominoAnnulledCreated
from domino.schemas.events.domino_rounds import DominoRoundsCreated, DominoRoundsAperture, BoletusPrinting

from domino.services.events.domino_round import get_all, get_one_by_id, start_one_round, get_info_to_aperture, \
    publicate_one_round, printing_all_boletus
    
from domino.services.events.domino_scale import get_all_players_by_tables, get_all_players_by_tables_and_round, \
    get_all_scale_by_round, get_all_tables_by_round, aperture_new_round, get_all_scale_by_round_by_pairs, close_one_round, \
    get_all_scale_acumulate, create_new_round, restart_one_round
from domino.services.events.domino_data import get_all_data_by_boletus, new_data, close_data_by_time, updated_data, reopen_one_boletus
from domino.services.events.domino_penalty import new as new_penalty, new_absences, get_penalty_by_boletus, \
    new_annulled, get_all_reason_no_update, remove_one_penalty
  
rounds_route = APIRouter(
    tags=["Rounds"],
    dependencies=[Depends(JWTBearer())]   
)

@rounds_route.get("/rounds/rounds/", response_model=Dict, summary="Obtain a list of Rounds.")
def get_rounds(
    request: Request,
    tourney_id: str,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, tourney_id=tourney_id, criteria_key=criteria_key, 
                   criteria_value=criteria_value, db=db, only_initiaded=False)
    
@rounds_route.get("/rounds/rounds/initiaded/", response_model=Dict, summary="Obtain a list of INITIADED Rounds.")
def get_rounds_initiaded(
    request: Request,
    tourney_id: str,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, tourney_id=tourney_id, criteria_key=criteria_key, 
                   criteria_value=criteria_value, db=db, only_initiaded=True)

@rounds_route.get("/rounds/rounds/one/", response_model=Dict, summary="Obtain info of Round.")
def get_one_round(
    round_id: str,
    db: Session = Depends(get_db)
):
    return get_one_by_id(round_id=round_id, db=db)

@rounds_route.get("/rounds/tables/", response_model=Dict, summary="Obtain a list of Tables at Rounds.")
def get_tables(
    request: Request,
    tourney_id: str,
    round_id: str = '',
    page: int = 1, 
    per_page: int = 6, 
    db: Session = Depends(get_db)
):
    return get_all_players_by_tables(request=request, tourney_id=tourney_id, round_id=round_id, page=page, per_page=per_page, db=db)

@rounds_route.get("/rounds/tables/one/", response_model=Dict, summary="Obtain a list of Tables of One Round.")
def get_tables_by_rounds(
    request: Request,
    round_id: str,
    page: int = 1, 
    per_page: int = 6, 
    db: Session = Depends(get_db)
):
    return get_all_players_by_tables_and_round(request=request, round_id=round_id, page=page, per_page=per_page, db=db)

@rounds_route.get("/rounds/scale/player/current/{id}", response_model=Dict, summary="Obtain Current Player ranking list")
def get_current_scale_by_rounds(
    request: Request,
    id: str,
    order: str = '1',
    page: int = 1, 
    per_page: int = 6, 
    db: Session = Depends(get_db)
):
    return get_all_scale_by_round(request=request, page=page, per_page=per_page, round_id=id, db=db, order=order)

@rounds_route.get("/rounds/scale/player/accumulated/{id}", response_model=Dict, summary="Obtain Accumulated Player ranking list")
def get_accumulated_scale_by_rounds(
    request: Request,
    id: str,
    page: int = 1, 
    per_page: int = 6, 
    db: Session = Depends(get_db)
):
    return get_all_scale_acumulate(request=request, page=page, per_page=per_page, round_id=id, db=db)

@rounds_route.get("/rounds/scale/player/pairs/{id}", response_model=Dict, summary="Obtain Player ranking list")
def get_scale_by_rounds(
    request: Request,
    id: str,
    page: int = 1, 
    per_page: int = 6, 
    db: Session = Depends(get_db)
):
    return get_all_scale_by_round_by_pairs(request=request, page=page, per_page=per_page, round_id=id, db=db)

@rounds_route.get("/rounds/boletus/all/{id}", response_model=Dict, summary="Obtain a list of Tables at Rounds.")
def get_tables(request: Request, id: str, page: int = 1, per_page: int = 6, db: Session = Depends(get_db)):
    return get_all_tables_by_round(request=request, round_id=id, page=page, per_page=per_page, db=db)

@rounds_route.get("/rounds/boletus/data/{id}", response_model=Dict, summary="Obtain a all datas of one boletus")
def get_tables(request: Request, id: str, db: Session = Depends(get_db)):
    return get_all_data_by_boletus(request=request, boletus_id=id, db=db)

@rounds_route.post("/rounds/boletus/data/{id}", response_model=ResultObject, summary="Insert Info of data")
def insert_data(request: Request, id: str, dominodata: DominoDataCreated, db: Session = Depends(get_db)):
    return new_data(request=request, boletus_id=id, dominodata=dominodata, db=db)

@rounds_route.put("/rounds/boletus/data/{id}", response_model=ResultObject, summary="Update Info of data")
def update_data(request: Request, id: str, dominodata: DominoDataCreated, db: Session = Depends(get_db)):
    return updated_data(request=request, data_id=id, dominodata=dominodata, db=db)

@rounds_route.post("/rounds/boletus/closedata/{id}", response_model=ResultObject, summary="Close data by time")
def close_data(request: Request, id: str, db: Session = Depends(get_db)):
    return close_data_by_time(request=request, boletus_id=id, db=db)

@rounds_route.get("/rounds/boletus/penalty/{id}", response_model=Dict, summary="Obtainf info of penalty of boletus")
def get_penalty(request: Request, id: str, db: Session = Depends(get_db)):
    return get_penalty_by_boletus(request=request, boletus_id=id, db=db)

@rounds_route.post("/rounds/boletus/penalty/{id}", response_model=ResultObject, summary="Insert New Penalty of player")
def insert_penalty(request: Request, id: str, dominopenalty: DominoPenaltiesCreated, db: Session = Depends(get_db)):
    return new_penalty(request=request, boletus_id=id, domino_penalty=dominopenalty, db=db)

@rounds_route.delete("/rounds/boletus/penalty/{id}", response_model=ResultObject, summary="Delete Info of Penalty")
def remove_penalty(request: Request, id: str, db: Session = Depends(get_db)):
    return remove_one_penalty(request=request, penalty_id=id, db=db)

@rounds_route.post("/rounds/boletus/absences/{id}", response_model=ResultObject, summary="Close Boletus por absences or abandon")
def insert_absences(request: Request, id: str, players: DominoAbsencesCreated, db: Session = Depends(get_db)):
    return new_absences(request=request, boletus_id=id, players=players, db=db)

@rounds_route.post("/rounds/boletus/annulled/{id}", response_model=ResultObject, summary="Annulled Boletus")
def insert_annulled(request: Request, id: str, domino_annulled: DominoAnnulledCreated, db: Session = Depends(get_db)):
    return new_annulled(request=request, boletus_id=id, domino_annulled=domino_annulled, db=db)

@rounds_route.get("/rounds/boletus/notupdate/{id}", response_model=Dict, summary="Get non-update reason")
def get_reason_noupdate(request: Request, id: str, db: Session = Depends(get_db)):
    return get_all_reason_no_update(request=request, boletus_id=id, db=db)

@rounds_route.post("/rounds/boletus/notupdate/{id}", response_model=Dict, summary="Reopen Boletus")
def clear_reason_noupdate(request: Request, id: str, db: Session = Depends(get_db)):
    return reopen_one_boletus(request=request, boletus_id=id, db=db)

@rounds_route.post("/rounds/boletus/printing/{id}", response_model=ResultObject, summary="Boletus printing")
def printing_boletus(request: Request, id: str, printing_boletus: BoletusPrinting, db: Session = Depends(get_db)):
    return printing_all_boletus(request=request, round_id=id, printing_boletus=printing_boletus, db=db)

@rounds_route.post("/rounds/actions/create/{tourney_id}", response_model=ResultObject, summary="Aperturate new Round not setting.")
def created_round(request: Request, tourney_id: str, db: Session = Depends(get_db)):
    return create_new_round(request=request, tourney_id=tourney_id, db=db)

@rounds_route.post("/rounds/actions/aperture/{id}", response_model=ResultObject, summary="Aperturate Round.")
def aperture_round(request: Request, id: str, round: DominoRoundsAperture, db: Session = Depends(get_db)):
    return aperture_new_round(request=request, round_id=id, round=round, db=db)

@rounds_route.get("/rounds/actions/aperture/{id}", response_model=Dict, summary="Obtain information to open Round.")
def get_info_aperture(request: Request, id: str, db: Session = Depends(get_db)):
    return get_info_to_aperture(request=request, round_id=id, db=db)

@rounds_route.post("/rounds/actions/publicate/{id}", response_model=ResultObject, summary="Publicate Round.")
def publicate_round(request: Request, id: str, db: Session = Depends(get_db)):
    return publicate_one_round(request=request, round_id=id, db=db)

@rounds_route.post("/rounds/actions/started/{id}", response_model=ResultObject, summary="Start Round.")
def start_round(request: Request, id: str, db: Session = Depends(get_db)):
    return start_one_round(request=request, round_id=id, db=db)

@rounds_route.post("/rounds/actions/close/{id}", response_model=ResultObject, summary="Close Round.")
def close_round(request: Request, id: str, db: Session = Depends(get_db)):
    return close_one_round(request=request, round_id=id, db=db)

@rounds_route.post("/rounds/actions/restart/{id}", response_model=ResultObject, summary="Restart Round.")
def restart_round(request: Request, id: str, db: Session = Depends(get_db)):
    return restart_one_round(request=request, round_id=id, db=db)




