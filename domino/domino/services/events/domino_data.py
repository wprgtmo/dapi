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

from domino.services.events.domino_boletus import get_one as get_one_boletus, get_one_boletus_pair
from domino.services.events.domino_scale import update_info_pairs, close_round_with_verify
from domino.services.resources.status import get_one_by_name as get_one_status_by_name
from domino.services.resources.utils import get_result_count
from domino.services.events.domino_round import calculate_amount_rounds_played, get_one as get_one_round, get_obj_info_to_aperturate
from domino.services.events.calculation_serv import get_motive_closed

def get_all_data_by_boletus(request:Request, boletus_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 
    
    str_from = "FROM events.domino_boletus_data ddata where boletus_id = '" + boletus_id + "' "
    str_count = "Select count(*) " + str_from
    str_query = "Select ddata.id as data_id, ddata.data_number, win_pair_id, number_points, duration " + str_from 
        
    result = get_result_count(page=0, per_page=0, str_count=str_count, db=db)
    
    str_query += " ORDER BY ddata.data_number ASC " 
    
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
    point_one_total, point_two_total = 0, 0
    for item in lst_data_exec:
        point_one, point_two = 0, 0
        if item.win_pair_id == dict_result['pair_one']['pairs_id']:
            point_one = item.number_points
            point_one_total += item.number_points
        else:
            point_two = item.number_points
            point_two_total += item.number_points
            
        lst_data.append({'number': item.data_number, 'pair_one': point_one, 'pair_two': point_two,
                         'data_id': item.data_id})
    
    dict_result['pair_one']['total_point'] = point_one_total
    dict_result['pair_two']['total_point'] = point_two_total
        
    dict_result['lst_data'] = lst_data
    
    dict_result['lst_players'] = get_info_player_of_boletus(boletus_id, db=db)
    
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

def get_info_player_of_boletus(boletus_id: str, db: Session):
    
    lst_data = []
    
    str_query = "SELECT single_profile_id, pmem.name, position_id FROM events.domino_boletus_position bpo " +\
        "join enterprise.profile_member pmem ON pmem.id = bpo.single_profile_id " +\
        "where boletus_id = '" + boletus_id + "' order by position_id "
        
    lst_data_exec = db.execute(str_query)
    for item in lst_data_exec:
        lst_data.append({'profile_id':  item.single_profile_id, 'profile_name': item.name, 'position_id': item.position_id})
    
    return lst_data

def get_one(data_id: str, db: Session):  
    return db.query(DominoBoletusData).filter(DominoBoletusData.id == data_id).first()
    
def new_data(request: Request, boletus_id:str, dominodata: DominoDataCreated, db: Session):
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    # buscar la boleta
    one_boletus = get_one_boletus(boletus_id, db=db)
    if not one_boletus:
        raise HTTPException(status_code=400, detail=_(locale, "boletus.not_found"))
    
    if one_boletus.status.name != 'INITIADED':
        raise HTTPException(status_code=404, detail=_(locale, "boletus.status_incorrect"))

    str_number = "SELECT data_number FROM events.domino_boletus_data where boletus_id = '" + boletus_id + "' " +\
        "ORDER BY data_number DESC LIMIT 1; "
    last_number = db.execute(str_number).fetchone()
    data_number = last_number[0] + 1 if last_number else 1
    
    one_data = DominoBoletusData(id=str(uuid.uuid4()), boletus_id=boletus_id, data_number=data_number, 
                                 win_pair_id=dominodata.pair, win_by_time=False, win_by_points=True,
                                 number_points=dominodata.point, duration=0)
    
    one_boletus.boletus_data.append(one_data)
    db.commit() 
    
    try:
        one_status_end = get_one_status_by_name('FINALIZED', db=db)
        result.data = close_boletus(one_boletus, currentUser['username'], db=db) 
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        msg = _(locale, "event.error_new_event")               
        raise HTTPException(status_code=403, detail=msg)
    
def verify_if_close_boletus(boletus_id:str, number_points_to_win: int, db: Session):
    
    str_query = "Select SUM(number_points) from events.domino_boletus_data " +\
        "Where boletus_id = '" + boletus_id + "' Group by win_pair_id " +\
        "Having SUM(number_points) >= " + str(number_points_to_win)
    points_max = db.execute(str_query).fetchone()
    return True if points_max else False

def verify_if_close_rounds(boletus_id:str, number_points_to_win: int, db: Session):
    
    str_query = "Select SUM(number_points) from events.domino_boletus_data " +\
        "Where boletus_id = '" + boletus_id + "' Group by win_pair_id " +\
        "Having SUM(number_points) >= " + str(number_points_to_win)
    points_max = db.execute(str_query).fetchone()
    
    return True if points_max else False

def close_data_by_time(request: Request, boletus_id:str, db: Session):
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    # buscar la boleta
    one_boletus = get_one_boletus(boletus_id, db=db)
    if not one_boletus:
        raise HTTPException(status_code=400, detail=_(locale, "boletus.not_found"))
    
    if one_boletus.status.name != 'INITIADED':
        raise HTTPException(status_code=404, detail=_(locale, "boletus.status_incorrect"))

    str_query = "Select win_pair_id, SUM(number_points) number_points from events.domino_boletus_data " +\
        "Where boletus_id = '" + boletus_id + "' Group by win_pair_id " 
    lst_pairs = db.execute(str_query)
    
    id_one_pair, id_two_pair = "", ""
    for item_pa in one_boletus.boletus_pairs:
        if not id_one_pair:
            id_one_pair = item_pa.pairs_id
        else:
            id_two_pair = item_pa.pairs_id
            
    points_one_pair, points_two_pair = 0, 0
    for item in lst_pairs:
        if item.win_pair_id == id_one_pair:
            points_one_pair += item.number_points
        else:
            points_two_pair += item.number_points
    
    if not points_one_pair and not points_two_pair:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.equal_positive_points"))
    
    if points_one_pair == points_two_pair: # estan empatados, no se puede cerrar
        raise HTTPException(status_code=404, detail=_(locale, "boletus.equal_positive_points"))
    
    if points_one_pair > points_two_pair:
        positive_points, negative_points = points_one_pair, points_two_pair
        win_pair_id, lost_pair_id = id_one_pair, id_two_pair
    else:
        positive_points, negative_points = points_two_pair, points_one_pair
        win_pair_id, lost_pair_id = id_two_pair, id_one_pair
    
    str_fields_win = "is_winner=True, positive_points = " + str(positive_points) + ", negative_points=" + str(negative_points)
    str_fields_win += " WHERE pairs_id = '" + win_pair_id + "'; "
    str_update_bol_win = "UPDATE events.domino_boletus_position SET " + str_fields_win 
    str_update_win = "UPDATE events.domino_boletus_pairs SET " + str_fields_win + str_update_bol_win
    
    str_fields_lost = "is_winner=False, positive_points = " + str(negative_points) + ", negative_points=" + str(positive_points)
    str_fields_lost += " WHERE pairs_id = '" + lost_pair_id + "'; "
    str_update_bol_lost = "UPDATE events.domino_boletus_position SET " + str_fields_lost 
    str_update_lost = "UPDATE events.domino_boletus_pairs SET " + str_fields_lost + str_update_bol_lost + "COMMIT;"
    
    str_update = str_update_win + str_update_lost
    
    try:
        db.execute(str_update)
        db.commit() 
    
        result.data = close_boletus(one_boletus, currentUser['username'], db=db, verify_points=False, motive_closed='time', can_update=False) 
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        msg = _(locale, "event.error_new_event")               
        raise HTTPException(status_code=403, detail=msg)
    
def close_boletus(one_boletus, username, db: Session, verify_points=True, motive_closed='points', can_update=True):
    
    # cuando cierra por tiempo siempre será True sta variable
    max_number_points = verify_if_close_boletus(one_boletus.id, one_boletus.tourney.number_points_to_win, db=db) if verify_points else True
    if max_number_points:
        motive_closed_description = get_motive_closed(motive_closed)
        one_status_end = get_one_status_by_name('FINALIZED', db=db)
        one_boletus.status_id = one_status_end.id
        one_boletus.updated_by = username
        one_boletus.updated_date = datetime.now()
        one_boletus.can_update = can_update
        one_boletus.motive_closed=motive_closed
        one_boletus.motive_closed_description=motive_closed_description
        db.add(one_boletus)
        db.commit() 
        
        amount_boletus_active = count_boletus_active(one_boletus.rounds.id, one_status_end, db=db)
        if amount_boletus_active == 0:  # ya todas están cerrados
            one_status_review = get_one_status_by_name('REVIEW', db=db)
            one_boletus.rounds.close_date = datetime.now()
            one_boletus.rounds.status_id = one_status_review.id
            one_boletus.rounds.updated_by = username
            one_boletus.rounds.updated_date = datetime.now()
            db.add(one_boletus.rounds)
            db.commit() 
    
    db_round_ini = get_one_round(round_id=one_boletus.round_id, db=db)
    result_data = get_obj_info_to_aperturate(db_round_ini, db) 
            
    return result_data
    
def updated_data(request: Request, data_id:str, dominodata: DominoDataCreated, db: Session):
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    # buscar la data
    one_data = get_one(data_id, db=db)
    if not one_data:
        raise HTTPException(status_code=400, detail=_(locale, "data.not_found"))
    
    #Puede modificarlo siempre que la ronda este en estado de revision o iniciada
    
    if one_data.boletus.rounds.status.name not in ('REVIEW', 'INITIADED'):
        raise HTTPException(status_code=404, detail=_(locale, "round.status_incorrect"))

    if one_data.win_pair_id != dominodata.pair:  #cambio la pareja que gana esa data
        one_data.win_pair_id = dominodata.pair
        
    if int(one_data.number_points) != int(dominodata.point):  
        one_data.number_points = dominodata.point
    
    db.add(one_data)
    db.commit()  
    
    str_query = "Select win_pair_id, SUM(number_points) number_points from events.domino_boletus_data " +\
        "Where boletus_id = '" + one_data.boletus.id + "' Group by win_pair_id " 
    lst_pairs = db.execute(str_query)
    
    points_one_pair, points_two_pair = 0, 0
    id_one_pair, id_two_pair = "", ""
    for item in lst_pairs:
        if not points_one_pair:
            points_one_pair += item.number_points
            id_one_pair = item.win_pair_id
        else:
            points_two_pair += item.number_points
            id_two_pair = item.win_pair_id
    
    # limpiar los ganadores por si acaso
    str_update = "UPDATE events.domino_boletus_pairs SET is_winner=False WHERE boletus_id = '" + one_data.boletus.id + "'; COMMIT;"
    db.execute(str_update)
            
    if points_one_pair >= one_data.boletus.tourney.number_points_to_win or points_two_pair >= one_data.boletus.tourney.number_points_to_win:
        
        # marcar como ganador la pareja que mas puntos tiene y cerrar la boleta
        if points_one_pair > points_two_pair:
            str_update = "UPDATE events.domino_boletus_pairs SET is_winner=True WHERE pairs_id ='" + id_one_pair + "'; COMMIT;"
        else:
            str_update = "UPDATE events.domino_boletus_pairs SET is_winner=True WHERE pairs_id ='" + id_two_pair + "'; COMMIT;"
            
            db.execute(str_update)
    
    else:
        str_update = "UPDATE events.domino_boletus_pairs SET is_winner=False WHERE pairs_id IN ('" + id_two_pair + "', '" + id_one_pair + "'); COMMIT;"
        db.execute(str_update)
        
        one_status_end = get_one_status_by_name('INITIADED', db=db)
        one_data.boletus.status_id = one_status_end.id
        one_data.boletus.updated_by = currentUser['username']
        one_data.boletus.updated_date = datetime.now()
        db.add(one_data.boletus)
        db.commit() 
        
    try:
        one_status_end = get_one_status_by_name('FINALIZED', db=db)
        result.data = close_boletus(one_data.boletus, currentUser['username'], db=db) 
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        msg = _(locale, "event.error_new_event")               
        raise HTTPException(status_code=403, detail=msg)
       
def count_boletus_active(round_id: str, status_end, db: Session):
    
    str_count = "SELECT count(id) FROM events.domino_boletus Where round_id = '" + round_id + "' AND status_id != " + str(status_end.id)
    amount_boletus = db.execute(str_count).fetchone()[0]
    return amount_boletus
