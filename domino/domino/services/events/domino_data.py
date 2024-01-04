import math
import uuid

from datetime import datetime
from fastapi import HTTPException, Request, UploadFile, File
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
import json
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.config.config import settings
from domino.app import _
from fastapi.responses import FileResponse
from os import getcwd

from domino.models.events.domino_data import DominoBoletusData

from domino.schemas.resources.result_object import ResultObject
from domino.schemas.events.domino_data import DominoDataCreated

from domino.services.events.domino_boletus import get_one as get_one_boletus
from domino.services.events.domino_scale import update_info_pairs, close_round_with_verify
from domino.services.resources.status import get_one_by_name as get_one_status_by_name
from domino.services.resources.utils import get_result_count

def get_all_data_by_boletus(request:Request, page: int, per_page: int, boletus_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 
    
    str_from = "FROM events.domino_boletus_data ddata where boletus_id = '" + boletus_id + "' "
    str_count = "Select count(*) " + str_from
    str_query = "Select ddata.data_number, win_pair_id, number_points, duration " + str_from 
        
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY ddata.data_number ASC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    db_boletus = get_one_boletus(boletus_id, db=db)
    if not db_boletus:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    dict_result = {'round_number': db_boletus.rounds.round_number, 'table_number': db_boletus.tables.table_number, 
                   'number_points_to_win': db_boletus.tourney.number_points_to_win,
                   'pair_one' : {'pairs_id': '', 'name': '', 'total_point': 0},
                   'pair_two' : {'pairs_id': '', 'name': '', 'total_point': 0}}
    
    dict_result = get_info_of_boletus(boletus_id, dict_result, db=db)
    
    lst_data_exec = db.execute(str_query)
    lst_data = []
    for item in lst_data_exec:
        point_one, point_two = 0, 0
        if item.win_pair_id == dict_result['pair_one']['pairs_id']:
            point_one = item.number_points
        else:
            point_two = item.number_points
            
        lst_data.append({'number': item.data_number, 'pair_one': point_one, 'pair_two': point_two})
        
    dict_result['lst_data'] = lst_data
    
    result.data = dict_result
    
    return result

def get_info_of_boletus(boletus_id: str, dict_result, db: Session):
    
    str_query = "Select pairs_id, positive_points, duration, dpair.name " +\
        "from events.domino_boletus_pairs dbpair " +\
        "join events.domino_boletus dbol ON dbol.id = dbpair.boletus_id " +\
        "join events.domino_rounds_pairs dpair ON dpair.id = dbpair.pairs_id " +\
        "where boletus_id = '" + boletus_id + "' "
        
    lst_data_exec = db.execute(str_query)
    pair_number = 1
    for item in lst_data_exec:
        if pair_number == 1:
            dict_result['pair_one']['pairs_id'] = item.pairs_id
            dict_result['pair_one']['name'] = item.name
            dict_result['pair_one']['total_point'] = int(item.positive_points) if item.positive_points else 0
            pair_number += 1
        else:
            dict_result['pair_two']['pairs_id'] = item.pairs_id
            dict_result['pair_two']['name'] = item.name
            dict_result['pair_two']['total_point'] = int(item.positive_points) if item.positive_points else 0
    
    return dict_result

def new_data(request: Request, boletus_id:str, dominodata: DominoDataCreated, db: Session):
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    # buscar la boleta
    one_boletus = get_one_boletus(boletus_id, db=db)
    if not one_boletus:
        raise HTTPException(status_code=400, detail=_(locale, "boletus.not_found"))
    
    one_status_init = get_one_status_by_name('INITIADED', db=db)
    if not one_status_init:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    if one_boletus.status_id != one_status_init.id:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.status_incorrect"))

    # cargar las boletas de las parejas para poder verificar si ya alguien gano y actualizar la info de la otra pareja
    lst_boletus_pair = one_boletus.boletus_pairs
    
    # if dominodata.close_for_time:
    #     close_data = True
    #     pass
    
    close_data = False
    pair_win, lost_pair = None, None
    # solo actualizo los puntos de la pareja ganadora
    for item in lst_boletus_pair:
        if item.pairs_id == dominodata.pair:
            item.positive_points = dominodata.point if not pair_win.positive_points else pair_win.positive_points + dominodata.point
            pair_win = item
        else:
            lost_pair = item
    
    str_number = "SELECT data_number FROM events.domino_boletus_data where boletus_id = '" + boletus_id + "' " +\
        "ORDER BY data_number DESC LIMIT 1; "
    last_number = db.execute(str_number).fetchone()
    data_number = last_number[0] + 1 if last_number else 1
    
    one_data = DominoBoletusData(id=str(uuid.uuid4()), boletus_id=boletus_id, data_number=data_number, 
                                 win_pair_id=dominodata.pair, win_by_time=False, win_by_points=True,
                                 number_points=dominodata.point, duration=0)
        
    close_data = True if pair_win.positive_points >= one_boletus.tourney.number_points_to_win else False
    
    result.data = {'closed_round': False}
    if close_data: 
        pair_win.positive_points = one_boletus.tourney.number_points_to_win
        pair_win.negative_points = lost_pair.positive_points
        lost_pair.negative_points = pair_win.positive_points
        pair_win.is_winner = True
            
        update_info_pairs(pair_win.pairs_id, lost_pair.pairs_id, dominodata.point, db=db)
        
        one_status_review = get_one_status_by_name('REVIEW', db=db)
        one_status_end = get_one_status_by_name('FINALIZED', db=db)
        if not one_status_review or not one_status_end:
            raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
        
        one_boletus.status_id = one_status_end.id
        one_boletus.updated_by = currentUser['username']
        one_boletus.updated_date = datetime.now()
        db.add(one_boletus)
        
        #verificar si ya llego fin del partido cerrar la ronda
        amount_boletus_active = count_boletus_active(one_boletus.rounds.id, one_status_end, db=db)
        if amount_boletus_active == 0:  # ya todas están cerrados
            one_boletus.rounds.close_date = datetime.now()
            one_boletus.rounds.status_id = one_status_review.id
            
            one_boletus.rounds.updated_by = currentUser['username']
            one_boletus.rounds.updated_date = datetime.now()
            
            db.add(one_boletus.rounds)
            
            result.data = {'closed_round': True}
    
    try:
        one_boletus.boletus_data.append(one_data)
        db.commit()            
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "event.error_new_event")               
        raise HTTPException(status_code=403, detail=msg)
    
def count_boletus_active(round_id: str, status_end, db: Session):
    
    str_count = "SELECT count(id) FROM events.domino_boletus Where round_id = '" + round_id + "' AND status_id != " + str(status_end.id)
    amount_boletus = db.execute(str_count).fetchone()[0]
    return amount_boletus
