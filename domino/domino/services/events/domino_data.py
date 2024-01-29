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

    # cargar las boletas de las parejas para poder verificar si ya alguien gano y actualizar la info de la otra pareja
    # lst_boletus_pair = one_boletus.boletus_pairs
    
    close_data = False
    # pair_win, lost_pair = None, None
    # solo actualizo los puntos de la pareja ganadora
    # for item in lst_boletus_pair:
    #     if item.pairs_id == dominodata.pair:
    #         # pair_win = item
    #         item.positive_points = dominodata.point if not pair_win.positive_points else pair_win.positive_points + dominodata.point
        # else:
        #     lost_pair = item
    
    str_number = "SELECT data_number FROM events.domino_boletus_data where boletus_id = '" + boletus_id + "' " +\
        "ORDER BY data_number DESC LIMIT 1; "
    last_number = db.execute(str_number).fetchone()
    data_number = last_number[0] + 1 if last_number else 1
    
    one_data = DominoBoletusData(id=str(uuid.uuid4()), boletus_id=boletus_id, data_number=data_number, 
                                 win_pair_id=dominodata.pair, win_by_time=False, win_by_points=True,
                                 number_points=dominodata.point, duration=0)
    
    one_boletus.boletus_data.append(one_data)
    db.commit() 
    
    # verificar si ya la boleta termino
    max_number_points = verify_if_close_boletus(one_boletus.id, one_boletus.tourney.number_points_to_win, db=db)
    if max_number_points:
        one_status_end = get_one_status_by_name('FINALIZED', db=db)
        one_boletus.status_id = one_status_end.id
        one_boletus.status_id = one_status_end.id
        one_boletus.updated_by = currentUser['username']
        one_boletus.updated_date = datetime.now()
        db.add(one_boletus)
        db.commit() 
        
        amount_boletus_active = count_boletus_active(one_boletus.rounds.id, one_status_end, db=db)
        if amount_boletus_active == 0:  # ya todas están cerrados
            one_status_review = get_one_status_by_name('REVIEW', db=db)
            one_boletus.rounds.close_date = datetime.now()
            one_boletus.rounds.status_id = one_status_review.id
            one_boletus.rounds.updated_by = currentUser['username']
            one_boletus.rounds.updated_date = datetime.now()
            db.add(one_boletus.rounds)
            db.commit() 
    
        
        # verificar si ya se cierra la ronda
        
    # close_data = True if pair_win.positive_points >= one_boletus.tourney.number_points_to_win else False
    # 
    # if close_data: 
        # pair_win.positive_points = one_boletus.tourney.number_points_to_win
        # pair_win.negative_points = lost_pair.positive_points
        # lost_pair.negative_points = pair_win.positive_points
        # pair_win.is_winner = True
        
        # acumulated_games_played = calculate_amount_rounds_played(one_boletus.tourney_id, db=db)
        
        # update_info_pairs(pair_win, lost_pair, one_boletus.tourney.number_points_to_win, db=db)
        
        # 
        # 
        # if not one_status_review or not one_status_end:
        #     raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
        
        
        
        #verificar si ya llego fin del partido cerrar la ronda
        
            
    try:
        
        db_round_ini = get_one_round(round_id=one_boletus.round_id, db=db)
        result.data = get_obj_info_to_aperturate(db_round_ini, db) 
               
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
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
    
    points_one_pair, points_two_pair = 0, 0
    id_one_pair, id_two_pair = "", ""
    for item in lst_pairs:
        if not points_one_pair:
            points_one_pair += item.number_points
            id_one_pair = item.win_pair_id
        else:
            points_two_pair += item.number_points
            id_two_pair = item.win_pair_id
    
    if not points_one_pair and not points_two_pair:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.equal_positive_points"))
    
    if points_one_pair == points_two_pair: # estan empatados, no se puede cerrar
        raise HTTPException(status_code=404, detail=_(locale, "boletus.equal_positive_points"))
    
    # marcar como ganador la pareja que mas puntos tiene y cerrar la boleta
    if points_one_pair > points_two_pair:
        str_update = "UPDATE events.domino_boletus_pairs SET is_winner=True WHERE pairs_id = '" + id_one_pair + "'; COMMIT;"
    else:
        str_update = "UPDATE events.domino_boletus_pairs SET is_winner=True WHERE pairs_id = '" + id_two_pair + "'; COMMIT;"
    db.execute(str_update)
        
    one_status_end = get_one_status_by_name('FINALIZED', db=db)
    one_boletus.status_id = one_status_end.id
    one_boletus.status_id = one_status_end.id
    one_boletus.updated_by = currentUser['username']
    one_boletus.updated_date = datetime.now()
    db.add(one_boletus)
    db.commit() 
    
    amount_boletus_active = count_boletus_active(one_boletus.rounds.id, one_status_end, db=db)
    if amount_boletus_active == 0:  # ya todas están cerrados
        one_status_review = get_one_status_by_name('REVIEW', db=db)
        one_boletus.rounds.close_date = datetime.now()
        one_boletus.rounds.status_id = one_status_review.id
        one_boletus.rounds.updated_by = currentUser['username']
        one_boletus.rounds.updated_date = datetime.now()
        db.add(one_boletus.rounds)
        db.commit() 
    
    try:
        
        db_round_ini = get_one_round(round_id=one_boletus.round_id, db=db)
        result.data = get_obj_info_to_aperturate(db_round_ini, db) 
               
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "event.error_new_event")               
        raise HTTPException(status_code=403, detail=msg)
    
    
    # pair_win.is_winner = True
    
    # one_boletus.status_id = one_status_end.id
    # one_boletus.updated_by = currentUser['username']
    # one_boletus.updated_date = datetime.now()
    # db.add(one_boletus)
    
    # round_id = one_boletus.round_id
        
    # cargar las boletas de las parejas para poder verificar si ya alguien gano y actualizar la info de la otra pareja
    # lst_boletus_pair = one_boletus.boletus_pairs
    
    # pair_one, pair_two = None, None
    # for item in lst_boletus_pair:
    #     if not pair_one:
    #         pair_one = item
    #     else:
    #         pair_two = item
    
    # if not pair_one.positive_points and not pair_two.positive_points:
    #     raise HTTPException(status_code=404, detail=_(locale, "boletus.equal_positive_points"))
    
    # pair_one.positive_points = 0 if not pair_one.positive_points else pair_one.positive_points  
    # pair_two.positive_points = 0 if not pair_two.positive_points else pair_two.positive_points  
      
    # if pair_one.positive_points and pair_two.positive_points:
    #     if pair_one.positive_points == pair_two.positive_points: # estan empatados, no se puede cerrar
    #         raise HTTPException(status_code=404, detail=_(locale, "boletus.equal_positive_points"))
    
    # if pair_one.positive_points > pair_two.positive_points:
    #     pair_win = pair_one 
    #     pair_lost = pair_two
    # else:
    #     pair_win = pair_two
    #     pair_lost = pair_one
    
    
        
    # pair_win.negative_points = pair_lost.positive_points
    # pair_lost.negative_points = pair_win.positive_points
    
    # pair_win.points_difference = round(pair_win.positive_points - pair_win.negative_points, 2)
    # pair_lost.points_difference = round(pair_lost.positive_points - pair_lost.negative_points, 2)
    
    # pair_win.is_winner = True
        
    # acumulated_games_played = calculate_amount_rounds_played(one_boletus.tourney_id, db=db)
    # update_info_pairs(pair_win, pair_lost, acumulated_games_played, one_boletus.tourney.constant_increase_elo, db=db)
    
    # one_status_review = get_one_status_by_name('REVIEW', db=db)
    # one_status_end = get_one_status_by_name('FINALIZED', db=db)
    # if not one_status_review or not one_status_end:
    #     raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    
    
    #verificar si ya llego fin del partido cerrar la ronda
    # amount_boletus_active = count_boletus_active(one_boletus.rounds.id, one_status_end, db=db)
    # if amount_boletus_active == 0:  # ya todas están cerrados
    #     one_boletus.rounds.close_date = datetime.now()
    #     one_boletus.rounds.status_id = one_status_review.id
        
    #     one_boletus.rounds.updated_by = currentUser['username']
    #     one_boletus.rounds.updated_date = datetime.now()
        
    #     db.add(one_boletus.rounds)
        
    # try:
    #     db.commit()   
        
    #     db_round_ini = get_one_round(round_id=round_id, db=db)
    #     result.data = get_obj_info_to_aperturate(db_round_ini, db)
                 
    #     return result
    # except (Exception, SQLAlchemyError, IntegrityError) as e:
    #     print(e)
    #     msg = _(locale, "event.error_new_event")               
    #     raise HTTPException(status_code=403, detail=msg)

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
            str_update = "UPDATE events.domino_boletus_pairs SET is_winner=True WHERE pairs_id '" + id_one_pair + "'; COMMIT;"
        else:
            str_update = "UPDATE events.domino_boletus_pairs SET is_winner=True WHERE pairs_id '" + id_two_pair + "'; COMMIT;"
            
            db.execute(str_update)
            
        one_status_end = get_one_status_by_name('FINALIZED', db=db)
        one_data.boletus.status_id = one_status_end.id
        one_data.boletus.status_id = one_status_end.id
        one_data.boletus.updated_by = currentUser['username']
        one_data.boletus.updated_date = datetime.now()
        db.add(one_data.boletus)
        db.commit() 
        
        amount_boletus_active = count_boletus_active(one_data.boletus.rounds.id, one_status_end, db=db)
        if amount_boletus_active == 0:  # ya todas están cerrados
            one_status_review = get_one_status_by_name('REVIEW', db=db)
            one_data.boletus.rounds.close_date = datetime.now()
            one_data.boletus.rounds.status_id = one_status_review.id
            one_data.boletus.rounds.updated_by = currentUser['username']
            one_data.boletus.rounds.updated_date = datetime.now()
            db.add(one_data.boletus.rounds)
            db.commit() 
    
    try:
        
        db_round_ini = get_one_round(round_id=one_data.boletus.round_id, db=db)
        result.data = get_obj_info_to_aperturate(db_round_ini, db) 
               
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "event.error_new_event")               
        raise HTTPException(status_code=403, detail=msg)
            
    # boletus_pairs = get_one_boletus_pair(one_data.boletus.id, one_data.win_pair_id, db=db)    
    # if int(one_data.number_points) != int(dominodata.point):
    #     diference = int(one_data.number_points) - int(dominodata.point)
    #     one_data.number_points = int(dominodata.point)
    #     boletus_pairs.positive_points -= diference
        
    # round_id = one_data.boletus.round_id
    # boletus_id = one_data.boletus.id
    # number_points_to_win = one_data.boletus.tourney.number_points_to_win
    
    # db.add(boletus_pairs)
    
        
    # db_round_ini = get_one_round(round_id=round_id, db=db)
     # total de puntos para ganar del torneo
     
    # one_pair_id = one_data.win_pair_id
    # two_pair_id = None
    
    # reconstruir los datos de las parejas
    # str_all_datas = "SELECT * FROM events.domino_boletus_data Where boletus_id = '" + boletus_id + "' " +\
    #     "ORDER BY data_number ASC "
    # lst_data = db.execute(str_all_datas).fetchall()
    # point_one_pair, poins_two_pair = 0, 0
    # str_datas_ok, pair_win_id = "", ""
    # for item_data in lst_data:
    #     str_datas_ok += " " + item_data.id
        
    #     if item_data.win_pair_id != one_pair_id:
    #         if not two_pair_id:
    #             two_pair_id = item_data.win_pair_id
    #         poins_two_pair += item_data.number_points
    #     else:
    #         point_one_pair += item_data.number_points
    #     if point_one_pair >= number_points_to_win or poins_two_pair >= number_points_to_win:  # ya alguien gano
    #         pair_win_id = one_pair_id if point_one_pair >= number_points_to_win else two_pair_id
    #         break
    
    # borrar si sobran datas
    # str_delete = ""
    # for item_data in lst_data:
    #     if item_data.id not in str_datas_ok:
    #         str_delete += "'" + item_data.id + "',"
        
    # if str_delete:    
    #     str_query_delete = "DELETE FROM events.domino_boletus_data where id IN (" + str_delete[:-1] + ");"
    #     str_query_delete += "UPDATE events.domino_boletus_pairs SET is_winner = True where boletus_id = '" + boletus_id +\
    #         "' AND pairs_id = '" + pair_win_id + "'; " +\
    #         ";COMMIT;"
        
    #     db.execute(str_query_delete)
            
    # acumulated_games_played = calculate_amount_rounds_played(one_boletus.tourney_id, db=db)
    # update_info_pairs(pair_win, lost_pair, acumulated_games_played, one_boletus.tourney.constant_increase_elo, db=db)
       
    # result.data = get_obj_info_to_aperturate(one_data.boletus.rounds, db) 
    
    #verificar si ya llego fin del partido cerrar la ronda
        # amount_boletus_active = count_boletus_active(one_boletus.rounds.id, one_status_end, db=db)
        # if amount_boletus_active == 0:  # ya todas están cerrados
        #     one_boletus.rounds.close_date = datetime.now()
        #     one_boletus.rounds.status_id = one_status_review.id
            
        #     one_boletus.rounds.updated_by = currentUser['username']
        #     one_boletus.rounds.updated_date = datetime.now()
            
        #     db.add(one_boletus.rounds)
    
    return result
       
def count_boletus_active(round_id: str, status_end, db: Session):
    
    str_count = "SELECT count(id) FROM events.domino_boletus Where round_id = '" + round_id + "' AND status_id != " + str(status_end.id)
    amount_boletus = db.execute(str_count).fetchone()[0]
    return amount_boletus
