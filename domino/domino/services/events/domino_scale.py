import math
import uuid
import random

from datetime import datetime
from fastapi import HTTPException, Request, UploadFile, File
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from typing import List, Dict
import json
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.config.config import settings
from domino.app import _
from fastapi.responses import FileResponse
from os import getcwd

from domino.models.events.domino_round import DominoRoundsScale, DominoRoundsPairs
from domino.models.events.tourney import TraceLotteryManual

from domino.schemas.events.domino_rounds import DominoManualScaleCreated, DominoRoundsAperture
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
from domino.services.enterprise.userprofile import get_one as get_one_profile
from domino.services.enterprise.auth import get_url_avatar

from domino.services.events.player import get_lst_id_player_by_elo, change_all_status_player_at_init_round, get_one_user, \
    get_lst_id_player_by_level, get_lst_id_player_with_boletus
from domino.services.events.domino_round import get_one as get_one_round, get_first_by_tourney, configure_rounds, configure_new_rounds, \
    get_obj_info_to_aperturate, remove_configurate_round, calculate_amount_rounds_played, configure_next_rounds, \
    get_last_by_tourney, calculate_amount_rounds_segmentated, get_str_to_order as get_str_to_order_round

from domino.services.events.domino_boletus import created_boletus_for_round, get_all_by_round
from domino.services.enterprise.auth import get_url_advertising
from domino.services.events.tourney import get_lst_categories_of_tourney, create_category_by_default, get_one as get_one_tourney, \
    get_str_to_order

from domino.services.events.calculation_serv import calculate_new_elo, calculate_score_expected, calculate_score_obtained, \
    calculate_increasing_constant, calculate_end_elo, format_number
    
def new_initial_manual_round(request: Request, tourney_id:str, dominoscale: list[DominoManualScaleCreated], db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 
    
    currentUser = get_current_user(request) 
    
    round_id, modality = get_round_to_configure(locale, tourney_id, db=db)
    one_status_init = get_one_status_by_name('INITIADED', db=db)
    
    initial_scale_by_manual_lottery(tourney_id, round_id, dominoscale, modality, db=db)
    
    configure_tables_by_round(tourney_id, round_id, modality, currentUser['username'], db=db)
    
    # cambiar estado del torneo a Iniciado
    str_update = "UPDATE events.tourney SET status_id=" + str(one_status_init.id) + " WHERE id = '" + tourney_id + "';"
    str_update += "UPDATE events.events SET status_id=" + str(one_status_init.id) + " WHERE id IN " +\
        "(Select tourney.event_id FROM events.tourney where id = '" + tourney_id + "');COMMIT;"
    db.execute(str_update)
    
    return result

def restart_one_initial_scale(request: Request, round_id:str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 
    
    db_round = get_one_round(round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_found"))
    
    if db_round.status.name == 'CONFIGURATED':
        # borrar todo lo que se configuro
        remove_configurate_round(db_round.tourney_id, db_round.id, db=db)
    
        db.commit()
    
    if db_round.tourney.lottery_type == 'AUTOMATIC':  # debo crera tood de nuevo otra vez
        round_created = DominoRoundsAperture(
            use_segmentation=db_round.tourney.use_segmentation, use_bonus=db_round.tourney.use_bonus,
            amount_bonus_tables=db_round.tourney.amount_bonus_tables, amount_bonus_points=db_round.tourney.amount_bonus_points)
        aperture_one_new_round(db_round.id, round_created, locale, db=db)
        
    # db_round_ini = get_one_round(round_id=round_id, db=db)
    # result.data = get_obj_info_to_aperturate(db_round_ini, db) 
    
    return result


def configure_tables_by_round(tourney_id:str, round_id: str, modality:str, created_by:str, db: Session, round_number:int=1, points_for_absences=200,
                              round_previous_id=None):
    
    if round_number == 1:
        update_elo_initial_scale(tourney_id, round_id, modality, db=db)
    
    #configurar parejas y rondas
    configure_rounds(tourney_id=tourney_id, round_id=round_id, modality=modality, created_by=created_by, db=db)
    
    #ubicar por mesas las parejas
    created_boletus_for_round(tourney_id=tourney_id, round_id=round_id, db=db, points_for_absences=points_for_absences)
    
    #calcular el SE de cada pareja y ponerselo a cada jugador...
    acumulated_games_played = calculate_amount_rounds_played(tourney_id=tourney_id, db=db)
    calculate_score_expeted_of_pairs(round_id=round_id, acumulated_games_played=acumulated_games_played, db=db)
    
    calculate_score_expeted_of_player_user(round_id=round_id, db=db, previous_round_id=round_previous_id)
    
    return True

def calculate_score_expeted_of_pairs(round_id:str, acumulated_games_played:int, db:Session):
    
    # obtener listado de todas las mesas con sus parejas, o sea cada boleta por mesa. 
    lst_boletus =  get_all_by_round(round_id, db=db)
    for item in lst_boletus:
        one_pair, two_pair = None, None
        elo_one_player_one_pair = 0
        elo_two_player_one_pair = 0
        elo_one_player_two_pair = 0
        elo_two_player_two_pair = 0
        for item_pair in item.boletus_pairs:
            if not one_pair:
                one_pair = item_pair
            else:
                two_pair = item_pair
        
        if one_pair:
            if one_pair.pair:
                if one_pair.pair.one_player_id:
                    str_query = "Select elo from events.players_users where profile_id =  '" + one_pair.pair.one_player_id + "'"
                    elo_one_player_one_pair = db.execute(str_query).fetchone()[0]
                
                if one_pair.pair.two_player_id:
                    str_query = "Select elo from events.players_users where profile_id =  '" + one_pair.pair.two_player_id + "'"
                    elo_two_player_one_pair = db.execute(str_query).fetchone()[0]
        
        if two_pair:  
            if two_pair.pair: 
                if two_pair.pair.one_player_id:
                    str_query = "Select elo from events.players_users where profile_id =  '" + two_pair.pair.one_player_id + "'"
                    elo_one_player_two_pair = db.execute(str_query).fetchone()[0]
                    
                if two_pair.pair.two_player_id:
                    str_query = "Select elo from events.players_users where profile_id =  '" + two_pair.pair.two_player_id + "'"
                    elo_two_player_two_pair = db.execute(str_query).fetchone()[0]
        
        elo_one_pair = round((elo_one_player_one_pair + elo_two_player_one_pair)/2, 4)
        elo_two_pair = round((elo_one_player_two_pair + elo_two_player_two_pair)/2, 4)
        
        se_one_pair = calculate_score_expected(elo_one_pair, elo_two_pair)
        se_two_pair = calculate_score_expected(elo_two_pair, elo_one_pair)
        
        str_update = "UPDATE events.domino_rounds_pairs SET "
        str_update_scale = "UPDATE events.domino_rounds_scale SET "
        
        str_one_pair = ''
        if one_pair:
            str_one_pair = str_update + "score_expected = " + str(se_one_pair) + ", elo_pair = " + str(elo_one_pair) + ", " +\
                "elo_pair_opposing = " + str(elo_two_pair) + ", acumulated_games_played = " + str(acumulated_games_played) +\
                ", elo_ra = 0 WHERE id = '" + one_pair.pairs_id + "'; "
        str_two_pair = ''
        if two_pair:    
            str_two_pair = str_update + "score_expected = " + str(se_two_pair) + ", elo_pair = " + str(elo_two_pair) + ", " +\
                "elo_pair_opposing = " + str(elo_one_pair) + ", acumulated_games_played = " + str(acumulated_games_played)+\
                ", elo_ra = 0 WHERE id = '" + two_pair.pairs_id + "'; " 
        
        str_execute =  str_one_pair + str_two_pair + " COMMIT;"
        db.execute(str_execute)
        
        str_one_player= ''
        if one_pair:
            str_where_one_pair = str(one_pair.pair.scale_id_one_player) + "','" +  str(one_pair.pair.scale_id_two_player) if \
                one_pair.pair.scale_id_two_player else str(one_pair.pair.scale_id_one_player)
            
            str_one_player = str_update_scale + "score_expected = " + str(se_one_pair) + ", games_played = " + str(acumulated_games_played) + ", " +\
                "acumulated_games_played = " + str(acumulated_games_played) + " WHERE id IN ('" + str_where_one_pair + "'); "
            
        str_two_player = ''
        if two_pair:  
            str_where_two_pair = str(two_pair.pair.scale_id_one_player) + "','" +  str(two_pair.pair.scale_id_two_player) if \
            two_pair.pair.scale_id_two_player else str(two_pair.pair.scale_id_one_player)
              
            str_two_player = str_update_scale + "score_expected = " + str(se_two_pair) + ", games_played = " + str(acumulated_games_played) + ", " +\
                "acumulated_games_played = " + str(acumulated_games_played) + " WHERE id IN ('" + str_where_two_pair + "'); "
        
        if str_one_player or str_two_player:       
            str_execute =  str_one_player + str_two_player + " COMMIT;"
            db.execute(str_execute)
                
    return True

def calculate_score_expeted_of_player_user(round_id:str, db:Session, previous_round_id: str=''):
         
    # actualizar la tabla de player_users
    str_player_user = "Update events.players_users puse SET games_played = sca.games_played, " +\
        "score_expected = puse.score_expected + sca.score_expected, category_id = sca.category_id, " +\
        "category_number = cat.position_number " +\
        "FROM events.domino_rounds_scale sca, events.domino_categories cat " +\
        "WHERE puse.player_id = sca.player_id and cat.id = sca.category_id  " +\
        "AND sca.round_id = '" + round_id + "';"
    
    str_elo_ra = ''
    if previous_round_id:
        str_elo_ra = "UPDATE events.players_users pu SET elo_ra = rs.elo_variable " +\
            "FROM events.domino_rounds_scale rs Where rs.player_id = pu.player_id " +\
            "And rs.round_id = '" + previous_round_id + "';"
        str_elo_ra += "Update events.domino_rounds_scale rsca_curr SET elo_ra = rsca_ant.elo_variable " +\
            "FROM events.domino_rounds_scale rsca_ant WHERE rsca_ant.player_id = rsca_curr.player_id " +\
            "AND rsca_ant.round_id = '" + previous_round_id + "' and rsca_curr.round_id = '" +\
            round_id + "';"
    
    str_update =  str_player_user  + str_elo_ra + "COMMIT;" 
    db.execute(str_update)
    
    db.commit()
    return True

def get_round_to_configure(locale, tourney_id:str, db: Session):
    
    # si el torneo ya tiene mas de una ronda no se puede hacer esto
    str_query = "Select count(*) FROM events.domino_rounds WHERE tourney_id = '" + tourney_id + "' "
    amount_round = db.execute(str_query).fetchone()[0]
    if amount_round != 1:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_initial_round"))
    
    str_query = "Select id FROM events.domino_rounds WHERE tourney_id = '" + tourney_id + "' and round_number = 1 "
    round_id = db.execute(str_query).fetchone()
    if not round_id:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_initial_round"))
    
    str_query = "Select modality FROM events.tourney WHERE id = '" + tourney_id + "' "
    modality = db.execute(str_query).fetchone()
    if not modality:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_initial_round"))
    
    return round_id[0], modality[0]

def update_elo_initial_scale(tourney_id: str, round_id: str, modality:str, db: Session ):
    
    str_scale = "Select player_id from events.domino_rounds_scale where tourney_id = '" + tourney_id + "' " +\
        "and round_id = '" + round_id + "' order by position_number ASC "
    
    lst_scale = db.execute(str_scale).fetchall()
    
    str_select = "Select Round(SUM(splay.elo)/2,4) as elo " if modality == 'Parejas' else 'Select splay.elo '
    str_select += "FROM events.players play JOIN enterprise.profile_users puse ON puse.profile_id = play.profile_id " +\
        "JOIN enterprise.profile_single_player splay ON splay.profile_id = puse.single_profile_id "
    
    str_update = "UPDATE events.domino_rounds_scale SET elo = "
    str_all_update = ''
    for item in lst_scale:
        str_find = str_select + " where id = '" + item.player_id + "' "
        elo = db.execute(str_find).fetchone()
        if elo:
            str_one_update = str_update + str(elo[0]) + " where player_id = '" + item.player_id + "'; "
            str_all_update += str_one_update
    
    if str_all_update:
        db.execute(str_all_update)
        db.commit()
        
    return True

def create_one_scale(tourney_id: str, round_id: str, round_number, position_number: int, player_id: str, category_id:str, db: Session, 
                     elo:float=None):
    one_scale = DominoRoundsScale(id=str(uuid.uuid4()), tourney_id=tourney_id, round_id=round_id, round_number=round_number, 
                                  position_number=int(position_number), player_id=player_id, is_active=True, category_id=category_id,
                                  elo=elo)
    db.add(one_scale)
        
    return True

def create_one_manual_trace(tourney_id: str, modality:str, position_number: int, player_id: str, db: Session ):
    
    one_trace = TraceLotteryManual(id=str(uuid.uuid4()), tourney_id=tourney_id, modality=modality, 
                                   position_number=int(position_number), player_id=player_id, is_active=True)
    db.add(one_trace)
        
    return True

def initial_scale_by_manual_lottery(tourney_id: str, round_id: str, dominoscale:list, modality:str, db: Session):
    
    for item in dominoscale:
        create_one_manual_trace(tourney_id, modality, int(item['position_number']), item['id'], db=db)
        create_one_scale(tourney_id, round_id, 1, int(item['position_number']), item['id'], category_id=item['category'], db=db)
    db.commit()
    return True

def configure_manual_lottery(db_round, dominoscale:list, db: Session, uses_segmentation=False):
    
    for item in dominoscale:
        create_one_manual_trace(db_round.tourney.id, db_round.tourney.modality, int(item['position_number']), item['id'], db=db)
        create_one_scale(db_round.tourney.id, db_round.id, 1, int(item['position_number']), item['id'], category_id=item['category'], db=db)
    db.commit()
    return True
    
def configure_automatic_lottery(db_round, db: Session, uses_segmentation=False):
    
    if uses_segmentation:
        # buscar las categorias definidas. 
        str_query = "SELECT * FROM events.domino_categories where tourney_id = '" + db_round.tourney.id + "' ORDER BY position_number "
        lst_categories = db.execute(str_query).fetchall()
    else:
        str_query = "SELECT * FROM events.domino_categories where by_default is True and tourney_id = '" +\
            db_round.tourney.id + "' ORDER BY position_number "
        lst_categories = db.execute(str_query).fetchall()
        
    if not lst_categories:  # crear la de por defecto
        create_category_by_default(db_round.tourney.id, db_round.tourney.elo_max, db_round.tourney.elo_min, None, db=db)
        str_query = "SELECT * FROM events.domino_categories where by_default is True and tourney_id = '" +\
            db_round.tourney.id + "' ORDER BY position_number "
        lst_categories = db.execute(str_query).fetchall()
    
    position_number=0
    for item_cat in lst_categories:   
        position_number=created_automatic_lottery(
            db_round.tourney.id, db_round.tourney.modality, db_round.id, item_cat.elo_min, item_cat.elo_max, position_number, item_cat.id, db=db,
            segmentation_type=db_round.tourney.segmentation_type)
        
    return True

def created_automatic_lottery(tourney_id: str, modality:str, round_id: str, elo_min:float, elo_max:float, position_number:int, 
                              category_id, db: Session, segmentation_type='ELO'):
    
    if segmentation_type == 'ELO':
        list_player = get_lst_id_player_by_elo(tourney_id, modality, min_elo=elo_min, max_elo=elo_max, db=db)
    elif segmentation_type == 'NIVEL':
        list_player = get_lst_id_player_by_level(tourney_id, modality, category_id, db=db)
    else:
        list_player = get_lst_id_player_with_boletus(tourney_id, db=db)
    
    lst_groups = sorted(list_player, key=lambda y:random.randint(0, len(list_player)))
    for item_pos in lst_groups:
        position_number += 1
        create_one_scale(tourney_id, round_id, 1, position_number, item_pos, category_id, db=db)
    db.commit()
    return position_number

def configure_new_lottery_by_round(db_round, db_round_new, modality:str, db: Session):
    
    # buscar las categorias definidas. 
    str_query = "SELECT * FROM events.domino_categories where tourney_id = '" + db_round.tourney_id + "' ORDER BY position_number"
    lst_categories = db.execute(str_query).fetchall()
    
    position_number = 0
    for item_cat in lst_categories:  
        position_number=created_automatic_lottery_by_round_cat(
            db_round.tourney_id, db_round.id, db_round_new.id, db_round_new.round_number, item_cat.id, position_number, db=db)
        
    configure_tables_by_round(db_round.tourney_id, db_round_new.id, modality, db_round.created_by, db=db)
    
    db.commit()
    
    return True

def close_round_with_verify(db_round: str, status_end, username: str, db: Session):
    
    str_count = "SELECT count(id) FROM events.domino_boletus Where round_id = '" + db_round.id + "' AND status_id != " + str(status_end.id)
    
    # verificar si ya todas las boletas cerraron, debemos cerrar la ronda.
    amount_boletus = db.execute(str_count).fetchone()[0]
    if amount_boletus != 0:
        return {'closed_round': False}
    
    db_round.close_date = datetime.now()
    
    last_number = db_round.round_number + 1
    
    # crear la nueva ronda
    # new_round = configure_new_rounds(db_round.tourney_id, 'Ronda Nro.' + str(last_number), db, created_by=username, round_number=last_number)
    
    # configure_new_lottery_by_round(db_round, new_round, db_round.tourney.modality, db=db)
    
    db_round.status_id = status_end.id
    if username:
        db_round.updated_by = username
    db_round.updated_date = datetime.now()
    
    db.add(db_round)
    db.commit()
    
    return {'closed_round': True}

def created_automatic_lottery_by_round_cat(tourney_id: str, round_id: str, new_round_id: str, new_round_number: int, category_id: str, 
                                       position_number:int, db: Session):
    
    list_player, dict_player = get_lst_player_by_scale_category(round_id, category_id, db=db)
    
    lst_groups = sorted(list_player, key=lambda y:random.randint(0, len(list_player)))
    for item_pos in lst_groups:
        position_number += 1
        create_one_scale(tourney_id, new_round_id, new_round_number, position_number, item_pos, category_id, db=db, elo=dict_player[item_pos])
    db.commit()
    return position_number

def get_lst_player_by_scale_category(round_id: str, category_id: str, db: Session):  
    
    str_query = "SELECT player_id, elo_variable FROM events.domino_rounds_scale WHERE is_active = True " +\
        "AND round_id = '" + round_id + "' AND category_id = '" + category_id + "' "
    lst_data = db.execute(str_query)
    dict_player = {}
    lst_players = []
    for item in lst_data:
        lst_players.append(item.player_id)
        dict_player[item.player_id] = item.elo_variable
    
    return lst_players, dict_player

def get_lst_players(tourney_id: str, round_id: str, db: Session):  
    return db.query(DominoRoundsScale).filter(DominoRoundsScale.tourney_id == tourney_id).\
        filter(DominoRoundsScale.round_id == round_id).order_by(DominoRoundsScale.position_number).all()
        
def get_lst_players_with_profile(tourney_id: str, round_id: str, db: Session):  
    
    lst_player = []
    
    str_query = "Select doms.player_id, puser.single_profile_id From events.domino_scale doms " +\
        "join events.players play ON play.id = doms.player_id " +\
        "join enterprise.profile_users puser ON puser.profile_id = play.profile_id " +\
        "Where doms.tourney_id = '" + tourney_id + "' and round_id = '" + round_id + "' "
    lst_result = db.execute(str_query)
    for item in lst_result:
        lst_player.append({'player_id': item.player_id, 'single_profile_id': item.single_profile_id})
    
    return lst_player

def get_all_players_by_tables(request:Request, page: int, per_page: int, tourney_id: str, round_id: str, db: Session):  
    
    # SI LA RONDA VIENE VACIA ES LA PRIMERA DEL TORNEO.
    
    if not round_id:
        db_round = get_first_by_tourney(tourney_id, db=db)
        round_id = db_round.id
    
    return get_all_players_by_tables_and_rounds(request, page, per_page=per_page, tourney_id=tourney_id, round_id=round_id, db=db)
        
def get_all_players_by_tables_and_round(request:Request, page: int, per_page: int, round_id: str, db: Session):  
    
    db_round = get_one_round(round_id, db=db)
    return get_all_players_by_tables_and_rounds(request, page, per_page=per_page, tourney_id=db_round.tourney_id, round_id=round_id, db=db)
    
def get_all_players_by_tables_and_rounds(request:Request, page: int, per_page: int, tourney_id: str, round_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    str_from = "FROM events.domino_boletus bol " +\
        "JOIN events.domino_tables dtab ON dtab.id = bol.table_id " +\
        "JOIN events.tourney tou ON tou.id = dtab.tourney_id " 
    
    str_count = "Select count(*) " + str_from
    str_query = "SELECT DISTINCT dtab.id as table_id, dtab.table_number, is_smart, dtab.image as table_image, " +\
        "tou.image as tourney_image, bol.id as boletus_id, dtab.tourney_id " + str_from
        
    str_where = "WHERE bol.is_valid is True AND dtab.is_active is True " + \
        "AND  dtab.tourney_id = '" + tourney_id + "' AND bol.round_id = '" + round_id + "' "
        
    str_count += str_where
    str_query += str_where + " ORDER BY dtab.table_number "

    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    
    lst_tables = []
    id=0
    for item in lst_data:
        
        table_image = get_url_advertising(tourney_id, item['table_image'] if item['table_image'] else item['tourney_image'], api_uri=api_uri)
        
        dict_tables = {'id': id, 'number': int(item['table_number']), 'table_id': item.table_id,
                       'type': "Inteligente" if item['is_smart'] else "Tradicional",
                       'image': table_image, 'boletus_id': item.boletus_id}
        
        dict_tables=create_dict_position(dict_tables, item.boletus_id, api_uri, db=db)
        lst_tables.append(dict_tables)
        id+=1
        
    result.data = lst_tables        
            
    return result

def get_all_scale_by_round(request:Request, page: int, per_page: int, round_id: str, db: Session, order='1'):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    str_from = "FROM events.domino_rounds_scale rsca " +\
        "JOIN events.players players ON players.id = rsca.player_id " +\
        "JOIN events.players_users pu ON players.id = pu.player_id " +\
        "jOIN resources.entities_status sta ON sta.id = players.status_id " +\
        "JOIN events.domino_categories cat ON cat.id = rsca.category_id " +\
        "JOIN enterprise.profile_member mmb ON players.profile_id = mmb.id " 
        
    str_count = "Select count(*) " + str_from
    str_query = "SELECT players.id player_id, mmb.id profile_id, mmb.name profile_name, mmb.photo, rsca.position_number, " +\
        "rsca.elo, rsca.elo_variable, rsca.games_played, rsca.elo_ra, pu.category_number, " +\
        "rsca.games_won, rsca.games_lost, rsca.points_positive, rsca.points_negative, rsca.points_difference, " +\
        "rsca.score_expected, rsca.score_obtained, rsca.k_value, rsca.elo_at_end, rsca.bonus_points, rsca.penalty_points, " +\
        "sta.id as status_id, sta.name as status_name, sta.description as status_description " + str_from
        
    str_where = "WHERE rsca.is_active is True AND rsca.round_id = '" + round_id + "' "
        
    str_count += str_where
    if order == '1': # posicion al inicio
        str_query += str_where + " ORDER BY rsca.position_number ASC "
    else:
        db_round = get_one_round(round_id, db=db)
        if db_round:
            str_query += str_where + get_str_to_order_round(db_round)
        else:
            str_query += str_where + " ORDER BY rsca.position_number ASC "
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    if page != 0:
        str_query += " LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_scale(item, db=db, api_uri=api_uri) for item in lst_data]
    
    return result

def get_all_scale_acumulate(request:Request, page: int, per_page: int, tourney_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    str_from = "FROM events.players_users rsca " +\
        "JOIN events.players players ON players.id = rsca.player_id " +\
        "JOIN enterprise.profile_member mmb ON players.profile_id = mmb.id " 
        
    str_count = "Select count(*) " + str_from
    str_query = "SELECT players.id player_id, mmb.id profile_id, mmb.name profile_name, mmb.photo, " +\
        "rsca.elo, rsca.elo_current, rsca.games_played, rsca.penalty_total penalty_points, " +\
        "rsca.games_won, rsca.games_lost, rsca.points_positive, rsca.points_negative, rsca.points_difference, " +\
        "score_expected, score_obtained, k_value, elo_at_end, bonus_points " + str_from
        
    str_where = "WHERE players.tourney_id = '" + tourney_id + "' "
    
    db_tourney = get_one_tourney(tourney_id, db=db)

    str_order_by = get_str_to_order(db_tourney)
        
    str_count += str_where
    str_query += str_where + str_order_by

    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    if page != 0:
        str_query += " LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    position_number = 0
    result.data = []
    for item in lst_data:
        position_number += 1
        result.data.append(create_dict_row_scale_acum(item, position_number, db=db, api_uri=api_uri))
    
    return result

def get_all_scale_by_round_by_pairs(request:Request, page: int, per_page: int, round_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    str_from = "FROM events.domino_rounds_pairs rspa " +\
        "JOIN events.domino_boletus_pairs ON domino_boletus_pairs.pairs_id = rspa.id " +\
        "JOIN events.domino_boletus ON domino_boletus.id = domino_boletus_pairs.boletus_id " +\
        "JOIN events.domino_tables ON domino_tables.id = domino_boletus.table_id " +\
        "left JOIN events.players players ON players.id = rspa.player_id " +\
        "left JOIN enterprise.profile_member mmb ON players.profile_id = mmb.id " 
        
    str_count = "Select count(*) " + str_from
        
    str_query = "SELECT rspa.id, rspa.name as profile_name, rspa.position_number, domino_tables.table_number, " +\
        "rspa.elo_pair, rspa.elo_pair_opposing, " +\
        "rspa.games_won, rspa.games_lost, rspa.points_positive, rspa.points_negative, rspa.points_difference, " +\
        "score_expected, score_obtained, k_value, elo_current, elo_at_end, bonus_points, elo_ra, rspa.penalty_points " + str_from
    
    str_where = "WHERE rspa.round_id = '" + round_id + "' "
        
    str_count += str_where
    str_query += str_where + " ORDER BY rspa.position_number "

    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_scale_pair(item, db=db) for item in lst_data]
    
    return result

def create_dict_row_scale(item, db: Session, api_uri):
    
    photo = get_url_avatar(item['profile_id'], item['photo'], api_uri=api_uri)
    
    new_row = {'id': item['player_id'], 'name': item['profile_name'], 
               'position_number': item['position_number'],
               'photo' : photo, 'elo': format_number(round(item['elo'],2)) if item['elo'] else 0, 
               'elo_variable': format_number(round(item['elo_variable'],2)) if item['elo_variable'] else 0,
               'games_played': item['games_played'] if item['games_played'] else 0, 
               'games_won': item['games_won'] if item['games_won'] else 0,
               'games_lost': item['games_lost'] if item['games_lost'] else 0, 
               'points_positive': item['points_positive'] if item['points_positive'] else 0,
               'points_negative': item['points_negative'] if item['points_negative'] else 0, 
               'points_difference': item['points_difference'] if item['points_difference'] else 0,
               'penalty_points': item['penalty_points'] if item['penalty_points']  else 0,
               'score_expected': format_number(round(item['score_expected'],2)) if item['score_expected'] else 0,
               'score_obtained': format_number(round(item['score_obtained'],2)) if item['score_obtained'] else 0,
               'k_value': format_number(round(item['k_value'],4)) if item['k_value'] else 0,
               'elo_at_end': format_number(round(item['elo_at_end'],2)) if item['elo_at_end'] else 0,
               'bonus_points': 0, 'elo_ra': format_number(round(item['elo_ra'],2)) if item['elo_ra'] else 0,
               'status_id': item['status_id'], 'status_name': item['status_name'], 
               'status_description': item['status_description']}
    
    return new_row

def create_dict_row_scale_acum(item, position_number, db: Session, api_uri):
    
    photo = get_url_avatar(item['profile_id'], item['photo'], api_uri=api_uri)
    
    new_row = {'id': item['player_id'], 'name': item['profile_name'], 
               'position_number': position_number,
               'photo' : photo, 'elo': format_number(round(item['elo'],2)) if item['elo'] else 0, 
               'elo_variable': format_number(round(item['elo_current'],2)) if item['elo_current'] else 0,
               'elo_at_end': format_number(round(item['elo_at_end'],2)),   
               'games_played': item['games_played'] if item['games_played'] else 0, 
               'games_won': item['games_won'] if item['games_won'] else 0,
               'games_lost': item['games_lost'] if item['games_lost'] else 0, 
               'points_positive': item['points_positive'] if item['points_positive'] else 0,
               'points_negative': item['points_negative'] if item['points_negative'] else 0, 
               'points_difference': item['points_difference'] if item['points_difference'] else 0,
               'penalty_points': item['penalty_points'] if item['penalty_points']  else 0,
               'penalty_total': item['penalty_points'] if item['penalty_points']  else 0,
               'score_expected': format_number(round(item['score_expected'],2)) if item['score_expected'] else 0,
               'score_obtained': format_number(round(item['score_obtained'],2)) if item['score_obtained'] else 0,
               'k_value': format_number(round(item['k_value'],2)) if item['k_value'] else 0,
               'elo_at_end': format_number(round(item['elo_at_end'],2)) if item['elo_at_end'] else 0,
               'bonus_points': 0}
    position_number += 1
    
    return new_row

def create_dict_row_scale_pair(item, db: Session):
       
    new_row = {'id': item['id'], 'name': item['profile_name'], 
               'position_number': item['position_number'],
               'table_number': item['table_number'],
               'elo_pair': format_number(round(item['elo_pair'],2)) if item['elo_pair'] else 0, 
               'elo_pair_opposing': format_number(round(item['elo_pair_opposing'],2)) if item['elo_pair_opposing'] else 0,
               'games_played': 1,
               'games_won': item['games_won'] if item['games_won'] else 0,
               'games_lost': item['games_lost'] if item['games_lost'] else 0, 
               'points_positive': item['points_positive'] if item['points_positive'] else 0,
               'points_negative': item['points_negative'] if item['points_negative'] else 0, 
               'points_difference': item['points_difference'] if item['points_difference'] else 0,
               'score_expected': format_number(round(item['score_expected'],2)) if item['score_expected'] else 0,
               'score_obtained': format_number(round(item['score_obtained'],2)) if item['score_obtained'] else 0,
               'k_value': item['k_value'] if item['k_value'] else 0,
               'elo_current': format_number(round(item['elo_current'],2)) if item['elo_current'] else 0,
               'elo_at_end': format_number(round(item['elo_at_end'],2)) if item['elo_at_end'] else 0,
               'elo_ra': format_number(round(item['elo_ra'],2)) if item['elo_ra'] else 0,
               'bonus_points': item['bonus_points'] if item['bonus_points'] else 0,
               'penalty_points': item['penalty_points'] if item['penalty_points'] else 0}
    
    return new_row

def create_dict_position(dict_tables, boletus_id: str, api_uri:str, db: Session):
    
    str_pos = "SELECT bpos.position_id, pro.name as profile_name, psin.elo, psin.level, " +\
        "bpos.single_profile_id, pro.photo, bpos.scale_number " +\
        "FROM events.domino_boletus_position bpos " +\
        "JOIN enterprise.profile_single_player psin ON psin.profile_id = bpos.single_profile_id " +\
        "JOIN enterprise.profile_member pro ON pro.id = psin.profile_id " +\
        "WHERE bpos.boletus_id = '" + boletus_id + "' ORDER BY bpos.position_id "
    lst_data = db.execute(str_pos)
    
    for item in lst_data:
        photo = get_url_avatar(item['single_profile_id'], item['photo'], api_uri=api_uri)
        dict_player = {'id': item.position_id, 'name': item.profile_name, 'elo': item.elo, 'nivel': item.level, 
                       'index': item.scale_number if item.scale_number else item.position_id, 'avatar': photo}
        
        if item.position_id == 1:
            dict_tables['playerOne'] = dict_player
        elif item.position_id == 2:  
            dict_tables['playerTwo'] = dict_player
        elif item.position_id == 3:
            dict_tables['playerThree'] = dict_player
        elif item.position_id == 4:  
            dict_tables['playerFour'] = dict_player
    
    return dict_tables

def get_all_tables_by_round(request:Request, page: int, per_page: int, round_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    api_uri = str(settings.api_uri) 
    
    str_from = "FROM events.domino_boletus dbol join events.domino_rounds dron ON dron.id = dbol.round_id " +\
        "join events.domino_tables dtable ON dtable.id = dbol.table_id " +\
        "Where dbol.round_id = '" + round_id + "' "
        
    str_count = "Select count(*) " + str_from
    str_query = "Select dron.round_number, dtable.table_number, dtable.is_smart, dbol.id as boletus_id, " +\
        "dbol.status_id, dbol.can_update " + str_from 
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY dtable.table_number ASC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data_exec = db.execute(str_query)
    
    lst_data = []
    one_status_init = get_one_status_by_name('INITIADED', db=db)
    
    for item in lst_data_exec:
        status_id = '0' if not item.status_id else '0' if item.status_id == one_status_init.id else '1'
        
        dict_inf_pair = get_info_of_boletus_pair(item.boletus_id, api_uri=api_uri, db=db)
        dict_inf_pair['round_number'] = item.round_number
        dict_inf_pair['table_number'] = item.table_number
        dict_inf_pair['table_type'] = 'Inteligente' if item.is_smart else 'Tradicional'
        dict_inf_pair['boletus_id'] = item.boletus_id
        dict_inf_pair['status'] = status_id
        dict_inf_pair['can_update'] = item.can_update 
        dict_inf_pair['status_partida'] = 'Partido Terminado' if status_id == '1' else 'Partido Jugando'
        lst_data.append(dict_inf_pair)
    
    result.data = lst_data
    return result

def get_info_of_boletus_pair(boletus_id: str, api_uri: str, db: Session):
    
    dict_result = {'pair_one' : {'name': '', 'player_one': '', 'player_two': '', 
                                 'avatar_one': '', 'avatar_two': '', 'elo_one': '', 'elo_two': '',
                                 'positive_point': 0, 'negative_point': 0, 'difference_point': 0,
                                 'is_winner': False},
                   'pair_two' : {'name': '', 'player_one': '', 'player_two': '', 
                                 'avatar_one': '', 'avatar_two': '', 'elo_one': '', 'elo_two': '',
                                 'positive_point': 0, 'negative_point': 0, 'difference_point': 0,
                                 'is_winner': False}}
    
    str_query = "Select dpair.name, pairs_id, dbpair.is_winner, sca_one.elo elo_one, sca_two.elo elo_two, " +\
        "pmone.name name_one, pmtwo.name name_two, " +\
        "pmone.photo photo_one, pmtwo.photo photo_two, pmone.id profile_id_one, pmtwo.id profile_id_two " +\
        "from events.domino_boletus_pairs dbpair " +\
        "join events.domino_boletus dbol ON dbol.id = dbpair.boletus_id " +\
        "join events.domino_rounds_pairs dpair ON dpair.id = dbpair.pairs_id " +\
        "left join events.domino_rounds_scale sca_one ON sca_one.id = dpair.scale_id_one_player " +\
        "left join events.domino_rounds_scale sca_two ON sca_two.id = dpair.scale_id_two_player " +\
        "left join enterprise.profile_member pmone ON pmone.id = dpair.one_player_id " +\
        "left join enterprise.profile_member pmtwo ON pmtwo.id = dpair.two_player_id " +\
        "where dbpair.boletus_id = '" + boletus_id + "' "
        
    lst_data_exec = db.execute(str_query)
    pair_number, pair_one_id, pair_two_id = 1, "", ""
    for item in lst_data_exec:
        if pair_number == 1:
            name_key = 'pair_one'
            pair_one_id = item.pairs_id
        else:
            name_key = 'pair_two' 
            pair_two_id = item.pairs_id
        
        dict_result[name_key]['name'] = item.name
        dict_result[name_key]['player_one'] = item.name_one
        dict_result[name_key]['player_two'] = item.name_two
        dict_result[name_key]['avatar_one'] = get_url_avatar(item.profile_id_one, item.photo_one, api_uri=api_uri)
        dict_result[name_key]['avatar_two'] = get_url_avatar(item.profile_id_two, item.photo_two, api_uri=api_uri)
        dict_result[name_key]['elo_one'] = item.elo_one
        dict_result[name_key]['elo_two'] = item.elo_two
        dict_result[name_key]['positive_point'] = 0 #int(item.positive_points) if item.positive_points else 0
        dict_result[name_key]['negative_point'] = 0 #int(item.negative_points) if item.negative_points else 0
        dict_result[name_key]['difference_point'] = 0 #dict_result[name_key]['positive_point'] - dict_result[name_key]['negative_point']
        dict_result[name_key]['is_winner'] = item.is_winner
        pair_number += 1
    
    str_points = "Select win_pair_id, SUM(bdata.number_points) as positive_points From events.domino_boletus_data bdata " +\
            "join events.domino_boletus dbol ON dbol.id = bdata.boletus_id where dbol.id = '" + boletus_id + "' group by win_pair_id "
    lst_points = db.execute(str_points)
    for item in lst_points:
        if item.win_pair_id == pair_one_id:
            dict_result['pair_one']['positive_point'] = item.positive_points
        else:
            dict_result['pair_two']['positive_point'] = item.positive_points
        
    if not dict_result['pair_one']['negative_point']:
        dict_result['pair_one']['negative_point'] = dict_result['pair_two']['positive_point']
        dict_result['pair_one']['difference_point'] = dict_result['pair_one']['positive_point'] - dict_result['pair_one']['negative_point']
        
    if not dict_result['pair_two']['negative_point']:
        dict_result['pair_two']['negative_point'] = dict_result['pair_one']['positive_point']
        dict_result['pair_two']['difference_point'] = dict_result['pair_two']['positive_point'] - dict_result['pair_two']['negative_point']
       
    return dict_result

def get_one_round_pair(id: str, db: Session):  
    return db.query(DominoRoundsPairs).filter(DominoRoundsPairs.id == id).first()

def get_one_round_scale(id: str, db: Session):  
    return db.query(DominoRoundsScale).filter(DominoRoundsScale.id == id).first()

def update_info_pairs_original(boletus_pair_win, boletus_pair_lost, number_points_to_win:int, db: Session):
    
    # actualizar los datos de la pareja ganadora en Round_pair
    round_win_pair = get_one_round_pair(boletus_pair_win.pairs_id, db=db)
    round_lost_pair = get_one_round_pair(boletus_pair_lost.pairs_id, db=db)

    scale_player_win_one = get_one_round_scale(round_win_pair.scale_id_one_player, db=db) 
    scale_player_win_two = get_one_round_scale(round_win_pair.scale_id_two_player, db=db)
    
    scale_player_lost_one = get_one_round_scale(round_lost_pair.scale_id_one_player, db=db)
    scale_player_lost_two = get_one_round_scale(round_lost_pair.scale_id_two_player, db=db)
    
    player_win_one = get_one_user(scale_player_win_one.player_id, round_win_pair.one_player_id, db=db) 
    player_win_two = get_one_user(scale_player_win_two.player_id, round_win_pair.two_player_id, db=db)
    
    player_lost_one = get_one_user(scale_player_lost_one.player_id, round_lost_pair.one_player_id, db=db)
    player_lost_two = get_one_user(scale_player_lost_two.player_id, round_lost_pair.two_player_id, db=db)
    
    round_win_pair.bonus_points = 0
    round_lost_pair.bonus_points = 0
    
    update_data_round_pair(boletus_pair_win, round_win_pair, number_points_to_win)
    update_data_round_pair(boletus_pair_lost, round_lost_pair, number_points_to_win)
    
    # actualizar los datos de la escala de la pareja
    update_data_round_scale(round_win_pair, scale_player_win_one, scale_player_win_two, True)
    update_data_round_scale(round_lost_pair, scale_player_lost_one, scale_player_lost_two, False)
    
    # actualizar los datos de los jugadores de cada pareja
    
    update_data_player(scale_player_win_one, player_win_one)
    update_data_player(scale_player_win_two, player_win_two)
    
    update_data_player(scale_player_lost_one, player_lost_one)
    update_data_player(scale_player_lost_two, player_lost_two)
    
    db.commit()
    
    return True

def update_info_pairs(boletus_pair_win, boletus_pair_lost, number_points_to_win:int, db: Session):
    
    # actualizar los datos de la pareja ganadora en Round_pair
    round_win_pair = get_one_round_pair(boletus_pair_win.pairs_id, db=db)
    round_lost_pair = get_one_round_pair(boletus_pair_lost.pairs_id, db=db)

    scale_player_win_one = get_one_round_scale(round_win_pair.scale_id_one_player, db=db) 
    scale_player_win_two = get_one_round_scale(round_win_pair.scale_id_two_player, db=db)
    
    scale_player_lost_one = get_one_round_scale(round_lost_pair.scale_id_one_player, db=db)
    scale_player_lost_two = get_one_round_scale(round_lost_pair.scale_id_two_player, db=db)
    
    player_win_one = get_one_user(scale_player_win_one.player_id, round_win_pair.one_player_id, db=db) 
    player_win_two = get_one_user(scale_player_win_two.player_id, round_win_pair.two_player_id, db=db)
    
    player_lost_one = get_one_user(scale_player_lost_one.player_id, round_lost_pair.one_player_id, db=db)
    player_lost_two = get_one_user(scale_player_lost_two.player_id, round_lost_pair.two_player_id, db=db)
    
    round_win_pair.bonus_points = 0
    round_lost_pair.bonus_points = 0
    
    update_data_round_pair(boletus_pair_win, round_win_pair, number_points_to_win)
    update_data_round_pair(boletus_pair_lost, round_lost_pair, number_points_to_win)
    
    # actualizar los datos de la escala de la pareja
    update_data_round_scale(round_win_pair, scale_player_win_one, scale_player_win_two, True)
    update_data_round_scale(round_lost_pair, scale_player_lost_one, scale_player_lost_two, False)
    
    # actualizar los datos de los jugadores de cada pareja
    
    update_data_player(scale_player_win_one, player_win_one)
    update_data_player(scale_player_win_two, player_win_two)
    
    update_data_player(scale_player_lost_one, player_lost_one)
    update_data_player(scale_player_lost_two, player_lost_two)
    
    db.commit()
    
    return True

def update_data_round_pair(boletus_pair, round_pair, number_points_to_win: int):
    
    round_pair.games_won = 1 if boletus_pair.is_winner else 0
    round_pair.games_lost = 1 if not boletus_pair.is_winner else 0
    
    round_pair.points_positive = boletus_pair.positive_points if boletus_pair.positive_points else 0
    round_pair.points_negative = boletus_pair.negative_points if boletus_pair.negative_points else 0
    round_pair.points_difference = round_pair.points_positive - round_pair.points_negative
    
    round_pair.score_obtained = calculate_score_obtained(round_pair.games_won, round_pair.points_difference, number_points_to_win)
    
    # round_pair.k_value = calculate_increasing_constant(constant_increase_elo, round_pair.acumulated_games_played)
    
    round_pair.elo_current = calculate_new_elo(
        round_pair.acumulated_games_played, round_pair.score_expected, round_pair.score_obtained)  
    round_pair.elo_at_end = round_pair.elo_pair + round_pair.elo_current
        
    return True

def update_data_round_scale(round_pair, scale_player_one, scale_player_two, is_winner: bool):
    
    scale_player_one.games_played, scale_player_two.games_played = 1, 1
    scale_player_one.games_won, scale_player_two.games_won = 1 if is_winner else 0, 1 if is_winner else 0
    scale_player_one.games_lost, scale_player_two.games_lost = 1 if not is_winner else 0, 1 if not is_winner else 0
    
    scale_player_one.points_positive, scale_player_two.points_positive = round_pair.points_positive, round_pair.points_positive
    scale_player_one.points_negative, scale_player_two.points_negative = round_pair.points_negative, round_pair.points_negative
    scale_player_one.points_difference, scale_player_two.points_difference = round_pair.points_difference, round_pair.points_difference
    
    scale_player_one.score_obtained, scale_player_two.score_obtained = round_pair.score_obtained, round_pair.score_obtained
    scale_player_one.acumulated_games_played = round_pair.acumulated_games_played
    scale_player_two.acumulated_games_played = round_pair.acumulated_games_played
    
    # scale_player_one.k_value = calculate_increasing_constant(constant_increase_elo, round_pair.acumulated_games_played)
    # scale_player_two.k_value = calculate_increasing_constant(constant_increase_elo, round_pair.acumulated_games_played)
    
    scale_player_one.elo_variable = round_pair.elo_current
    scale_player_two.elo_variable = round_pair.elo_current
    
    scale_player_one.elo_at_end = scale_player_one.elo + scale_player_one.elo_variable
    scale_player_two.elo_at_end = scale_player_two.elo + scale_player_two.elo_variable
    
    scale_player_one.bonus_points, scale_player_two.bonus_points = round_pair.bonus_points, round_pair.bonus_points
     
    return True

def update_data_player(scale_player, player):
    
    player.games_played = 1 if not player.games_played else player.games_played  + 1
    player.games_won = scale_player.games_won if not player.games_won else player.games_won + scale_player.games_won
    player.games_lost = scale_player.games_lost if not player.games_lost else player.games_lost + scale_player.games_lost
    
    player.points_positive = scale_player.points_positive if not player.points_positive else player.points_positive + scale_player.points_positive
    player.points_negative = scale_player.points_negative if not player.points_negative else player.points_negative + scale_player.points_negative
    points_difference = player.points_positive - player.points_negative
    player.points_difference = points_difference if not player.points_difference else player.points_difference + points_difference
    
    player.score_obtained = scale_player.score_obtained if not player.score_obtained else player.score_obtained + scale_player.score_obtained
    
    player.elo_current = scale_player.elo_variable if not player.elo_current else player.elo_current + scale_player.elo_variable
    player.elo_at_end = player.elo + player.elo_current
    
    player.bonus_points = scale_player.bonus_points if not player.bonus_points else round(player.bonus_points + scale_player.bonus_points, 4)
     
    return True

def get_values_elo_by_scale(round_id: str, db: Session):  
    
    str_query = "SELECT MAX(elo_variable) elo_max, MIN(elo_variable) elo_min " +\
        "FROM events.domino_rounds_scale Where round_id = '" + round_id + "' "
    
    lst_data = db.execute(str_query)
    elo_max, elo_min = float(0.00), float(0.00)
    for item in lst_data:
        elo_max = item.elo_max
        elo_min = item.elo_min
    
    return elo_max, elo_min

def create_new_round(request:Request, tourney_id:str, db:Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    db_round_last = get_last_by_tourney(tourney_id, db=db)
    db_round_next = configure_next_rounds(db_round_last, db=db)
    
    configure_tables_by_round(db_round_next.tourney.id, db_round_next.id, db_round_next.tourney.modality, db_round_next.tourney.updated_by, db=db)
    
    change_all_status_player_at_init_round(db_round_next, db=db)
    
    db_round_ini = get_one_round(round_id=db_round_next.id, db=db)
    result.data = get_obj_info_to_aperturate(db_round_ini, db) 
            
    return result

def aperture_new_round(request:Request, round_id:str, round: DominoRoundsAperture, db:Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    return aperture_one_new_round(round_id, round, locale, db=db)
    
def aperture_one_new_round(round_id:str, round_aperture: DominoRoundsAperture, locale, db:Session):
    # si la ronda no se ha publicado, puede eliminarse y volver a configurar..
    
    result = ResultObject() 
    
    db_round = get_one_round(round_id=round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_found"))
    
    one_status_created = get_one_status_by_name('CREATED', db=db)
    if not one_status_created:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    one_status_conf = get_one_status_by_name('CONFIGURATED', db=db)
    if not one_status_conf:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    if db_round.status.name not in ('CREATED', 'CONFIGURATED'):
        raise HTTPException(status_code=404, detail=_(locale, "round.status_incorrect"))
    
    info_round = get_obj_info_to_aperturate(db_round, db) 
    
    if info_round.amount_players_playing < 8:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.amount_player_incorrect"))
    
    if db_round.status.name == 'CONFIGURATED':
        remove_configurate_round(db_round.tourney_id, db_round.id, db=db)
    
    db_round.use_segmentation = True if db_round.tourney.use_segmentation and db_round.tourney.use_segmentation else False 
    
    if db_round.is_first:
        # sino usas las categorias en la primera, borro si tiene configuradas y creo una por defecto.
        if db_round.tourney.use_segmentation:
            # validar todas las categorias estén contempladas entre los elo de los jugadores.
            lst_category = get_lst_categories_of_tourney(tourney_id=db_round.tourney.id, db=db)
            if db_round.tourney.segmentation_type == 'ELO':
                if not verify_category_is_valid(float(db_round.tourney.elo_max), float(db_round.tourney.elo_min), lst_category=lst_category):
                    raise HTTPException(status_code=400, detail=_(locale, "tourney.setting_category_incorrect"))
        else:
            create_category_by_default(
                db_round.tourney.id, db_round.tourney.elo_max, db_round.tourney.elo_min, info_round.amount_players_playing, db=db)
        
        result_init = order_round_to_init(db_round, db=db, uses_segmentation=db_round.tourney.use_segmentation, round_aperture=round_aperture)
        if not result_init:
            raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_initial_scale_failed"))

    else:
        result_init = order_round_to_play(db_round, db=db)
        if not result_init:
            raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_initial_scale_failed"))
    
    configure_tables_by_round(db_round.tourney.id, db_round.id, db_round.tourney.modality, db_round.tourney.updated_by, db=db,
                              points_for_absences=db_round.tourney.points_for_absences)
    
    db_round.status_id = one_status_conf.id
    db_round.tourney.status_id = one_status_conf.id
    
    change_all_status_player_at_init_round(db_round, db=db)
     
    db.add(db_round)
    db.add(db_round.tourney)
    
    db.commit()
    
    db_round_ini = get_one_round(round_id=round_id, db=db)
    result.data = get_obj_info_to_aperturate(db_round_ini, db) 
    
    return result

def close_one_round(request: Request, round_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    db_round = get_one_round(round_id=round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_found"))
    
    # if db_round.status.name != 'REVIEW':
    #     raise HTTPException(status_code=404, detail=_(locale, "round.status_incorrect"))
    
    status_init = get_one_status_by_name('FINALIZED', db=db)
    
    db_round.status_id = status_init.id
    db_round.updated_by = currentUser['username']
    db_round.updated_date = datetime.now()
    db_round.close_date = datetime.now()
    
    count_round = calculate_amount_rounds_played(db_round.tourney.id, db=db)
    open_round = True if int(count_round) <= int(db_round.tourney.number_rounds) else False
    
    calculate_stadist_of_round(db_round, db=db)
    if open_round:
        if db_round.tourney.use_segmentation:
            # verificar si ya excedió la cantidad de rondas a bonificar
            count_seg_round = calculate_amount_rounds_segmentated(db_round.tourney.id, db=db)
            if count_seg_round + 1 > db_round.tourney.amount_segmentation_round:
                db_round.tourney.use_segmentation = False
                db.add(db_round.tourney)
        
        db_round_next = configure_next_rounds(db_round, db=db)
        
        configure_tables_by_round(db_round_next.tourney.id, db_round_next.id, db_round_next.tourney.modality, db_round_next.tourney.updated_by, db=db,
                                  round_previous_id=db_round.id)
    
        change_all_status_player_at_init_round(db_round_next, db=db)
        
        db_round_ini = get_one_round(round_id=db_round_next.id, db=db)
        result.data = get_obj_info_to_aperturate(db_round_ini, db) 
    
    else:
        db_round.is_last = True
        db.add(db_round)
        db.commit()
        
        result.data = get_obj_info_to_aperturate(db_round, db) 
            
    return result

def restart_one_round(request: Request, round_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    db_round = get_one_round(round_id=round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_found"))
    
    tourney_id = db_round.tourney_id
    
    # sumar el acumulado de los jugadores hasta la ronda anterior
    
    str_where = "WHERE round_id = '" + db_round.id + "'; "
    str_join = " WHERE ba.boletus_id IN (SELECT id FROM events.domino_boletus " + str_where[:-2] + "); " 

    str_delete = "DELETE FROM events.domino_boletus_penalties ba " + str_join +\
        "DELETE FROM events.domino_boletus_data ba " + str_join +\
        "DELETE FROM events.domino_boletus_position ba " + str_join +\
        "DELETE FROM events.domino_boletus_pairs ba " + str_join +\
        "DELETE FROM events.domino_boletus " + str_where  +\
        "DELETE FROM events.domino_rounds_pairs " + str_where +\
        " DELETE FROM events.domino_rounds_scale " + str_where  +\
        "DELETE FROM events.domino_rounds WHERE id = '" + db_round.id + "'; COMMIT;"
    db.execute(str_delete)
    
    db_current_round = get_last_by_tourney(tourney_id, db=db)
    if db_current_round:
    
        status_review = get_one_status_by_name('REVIEW', db=db)
        db_current_round.status_id = status_review.id
        db_current_round.updated_by = currentUser['username']
        db_current_round.updated_date = datetime.now()
        db_current_round.close_date = datetime.now()
        
    db.commit()
    
    return result

def calculate_stadist_of_boletus(one_boletus, db:Session):
    
    # este metodo lo voy a llmar cada vez que cierre ua boleta.
    if one_boletus.status.name != 'FINALIZED':
        return False
    
    if one_boletus.motive_closed == 'points':
        
        id_one_pair, id_two_pair = "", ""
        for item_pa in one_boletus.boletus_pairs:
            if not id_one_pair:
                id_one_pair = item_pa.pairs_id
            else:
                id_two_pair = item_pa.pairs_id
            
        str_query = "Select win_pair_id, SUM(number_points) number_points from events.domino_boletus_data " +\
            "Where boletus_id = '" + one_boletus.id + "' group by win_pair_id "
        lst_points = db.execute(str_query).fetchone()
        points_one_pair, points_two_pair = 0, 0
        for item_da in lst_points:
            if item_da.win_pair_id == id_one_pair:
                points_one_pair += item_da.number_points
            else:
                points_two_pair += item_da.number_points
        
        str_query = "Select single_profile_id, SUM(penalty_value) penalty_value FROM events.domino_boletus_penalties bpe " +\
           "Where boletus_id = '" + one_boletus.id + "' group by single_profile_id " 
        lst_penalty = db.execute(str_query).fetchone()
        for item_pe in lst_penalty:
            dict_penalty[item_pe.single_profile_id] = int(item_pe.penalty_value)
            
        # consulta de updates datos
        
    return True

def calculate_stadist_of_players(db_round, db:Session):
    
    # falta tema penalizaciones
    
    lst_boletus = get_all_by_round(db_round.id, db=db)
    for item_bol in lst_boletus:
        
        one_pair, two_pair = None, None
        one_points_pair, two_points_pair = 0, 0
        position_number = 1
        for item_pair in item_bol.boletus_pairs:
            
            # sumar todos los puntos de cada pareja por datas
            str_query = "Select SUM(number_points) number_points from events.domino_boletus_data " +\
                "Where win_pair_id = '" + item_pair.pairs_id + "' "
            sum_points = db.execute(str_query).fetchone()[0]
            
            if position_number == 1:
                one_pair = item_pair
                one_points_pair = sum_points if sum_points else 0
                position_number += 1
            else:
                two_pair = item_pair
                two_points_pair = sum_points if sum_points else 0
        
        # No truncar la cantidad de puntos sino ponerlos todos los que cogieron
        ## one_points_pair = one_points_pair if one_points_pair <= db_round.tourney.number_points_to_win else db_round.tourney.number_points_to_win 
        # two_points_pair = two_points_pair if two_points_pair <= db_round.tourney.number_points_to_win else db_round.tourney.number_points_to_win   
             
        one_pair.positive_points = one_points_pair
        one_pair.negative_points = two_points_pair
        one_pair.points_difference = one_points_pair - two_points_pair
        
        boletus_pair_win, boletus_pair_lost = None, None
        if two_pair:
            two_pair.positive_points = two_points_pair
            two_pair.negative_points = one_points_pair
            two_pair.points_difference = two_points_pair - one_points_pair
        
            if one_pair.positive_points > two_pair.positive_points:
                one_pair.is_winner = True
                boletus_pair_win = one_pair
                boletus_pair_lost = two_pair
            else:
                two_pair.is_winner = True
                boletus_pair_win = two_pair
                boletus_pair_lost = one_pair
        else:
            one_pair.is_winner = True
            boletus_pair_win = one_pair
            boletus_pair_lost = None
        
        update_info_pairs(boletus_pair_win, boletus_pair_lost, db_round.tourney.number_points_to_win, db=db)
            
        db.commit()
         
    return True

def calculate_stadist_of_round(db_round, db:Session):
    
    str_query_pair = "Select id, elo_pair, score_expected, games_won, games_lost, points_positive, points_negative, points_difference " +\
        "From events.domino_rounds_pairs where round_id = '" + db_round.id + "'"
    lst_res_pair = db.execute(str_query_pair) 
    str_update = ""
    for item in lst_res_pair:
        score_obtenied = calculate_score_obtained(
            item.games_won if item.games_won else 0, item.points_difference if item.points_difference else 0, db_round.tourney.number_points_to_win)
        k_value = db_round.tourney.constant_increase_elo   # realizo calculo para jugadores
        elo_current = calculate_new_elo(item.games_won if item.games_won else 0, item.score_expected, score_obtenied)
        elo_end = item.elo_pair + elo_current
        str_update += "Update events.domino_rounds_pairs SET score_obtained=" + str(score_obtenied) + ", k_value=" + str(k_value) +\
            ", elo_current =" + str(round(elo_current,4)) + ", elo_at_end = " + str(elo_end) +\
            " WHERE id = '" + item.id + "'; "
    if str_update:  
        db.execute(str_update)  
          
    str_query_pair = "Select sca.id, player_id, elo, score_expected, games_won, games_lost, points_positive, points_negative, points_difference " +\
        ", penalty_points, cat.position_number, cat.id as category_id, elo_ra " +\
        "From events.domino_rounds_scale sca left join events.domino_categories cat ON cat.id = " +\
        "sca.category_id where round_id = '" + db_round.id + "'"
    lst_res_play = db.execute(str_query_pair) 
    str_update = ""
    
    # No me hace falta quitarle la categoria, simplemente después para ordenar no utilizo este campo y ya...
    for item in lst_res_play:
        score_obtenied = calculate_score_obtained(
            item.games_won if item.games_won else 0, item.points_difference if item.points_difference else 0, db_round.tourney.number_points_to_win)
        k_value = db_round.tourney.constant_increase_elo   # realizo calculo para jugadores
        elo_current = calculate_new_elo(item.games_won if item.games_won else 0, item.score_expected, score_obtenied)
        elo_end = calculate_end_elo(item.elo, elo_current, db_round.tourney.constant_increase_elo)
        str_update += "Update events.domino_rounds_scale SET score_obtained=" + str(score_obtenied) + ", k_value=" + str(k_value) +\
            ", elo_variable =" + str(round(elo_current,4)) + ", elo_at_end = " + str(elo_end) +\
            " WHERE id = '" + item.id + "'; "
        # category_id = str(item.category_id) if item.category_id else "''"
        # category_number = str(item.position_number) if item.position_number else '1'
        elo_ra = str(item.elo_ra) if item.elo_ra else "0"
        penalty_points = str(item.penalty_points) if item.penalty_points else "0"
        
        str_update += "Update events.players_users SET elo_current = elo_current + " + str(round(elo_current,4)) +\
            ", elo_at_end = elo_at_end + " + str(elo_end) + ", games_played = games_played + 1, games_won = games_won + " +\
            str(item.games_won) + ", games_lost = games_lost + " + str(item.games_lost) +\
            ", points_positive = points_positive + " + str(item.points_positive) + ", points_negative = points_negative + " +\
            str(item.points_negative) + ", points_difference = points_difference + " + str(item.points_difference) +\
            ", score_expected = score_expected + " + str(item.score_expected) + ", score_obtained = score_obtained + " +\
            str(score_obtenied) +  ", k_value = " + str(k_value) + ", penalty_total = penalty_total + " +\
            penalty_points + ", elo_ra = " + elo_ra + " WHERE player_id = '" + item.player_id + "'; "
    if str_update:  
        db.execute(str_update)  
          
    db.commit()
         
    return True
      
def verify_category_is_valid(elo_max: float, elo_min: float, lst_category: list):
    
    current_elo_max = float(elo_max)
    current_elo_min = float(elo_min)
    
    for item in lst_category:
        if str(float(current_elo_max)) !=  str(float(item['elo_max'])):
            return False
        else:
            current_elo_max = float(float(item['elo_min']) - 1) 
            current_elo_min = float(item['elo_min'])
    
    # if str(float(current_elo_min)) != str(float(elo_min)) and current_elo_min < elo_min:
    if current_elo_min < elo_min:
        return False
    
    return True

def order_round_to_init(db_round, db:Session, round_aperture: DominoRoundsAperture, uses_segmentation=False):
    
    if db_round.tourney.lottery_type == "MANUAL":
        # salvar la escala manual en trazas
        result_init = configure_manual_lottery(db_round, round_aperture.lottery, db=db)
    else:
        result_init = configure_automatic_lottery(db_round, db=db, uses_segmentation=uses_segmentation)
            
    if not result_init:
        return False
    
    return True   

def order_round_to_play(db_round, db:Session, uses_segmentation=True):
    
    result_init = configure_automatic_lottery(db_round, db=db, uses_segmentation=uses_segmentation)
    
    if not result_init:
        return False
    
    return True  

def order_round_to_end(db_round, db:Session, uses_segmentation=False):
    
    return True 

# def remove_configurate_round(tourney_id: str, round_id: str, db: Session):
    
#     str_round = "WHERE round_id = '" + round_id + "'; "
#     str_id_boletus = "(SELECT id from events.domino_boletus where round_id = '" + round_id + "') "
    
#     # if manual la loteria y se va a borrar tambien se pone sino NO.
    
#     #Posicionamiento
#     str_loterry = "DELETE FROM events.trace_lottery_manual WHERE touney_id = '" + tourney_id + "'; " 
#     str_scale = "DELETE FROM events.domino_rounds_scale " + str_round +\
#         "DELETE FROM events.domino_rounds_pairs " + str_round
    
#     #boleta
#     domino_boletus = "DELETE from events.domino_boletus_position where boletus_id IN " + str_id_boletus + "; " +\
#         "DELETE from events.domino_boletus_data where boletus_id IN " + str_id_boletus + "; " +\
#         "DELETE from events.domino_boletus_pairs where boletus_id IN " + str_id_boletus + "; "
        
#     domino_boletus += "DELETE FROM events.domino_boletus where round_id = '" + round_id + "'; " 
    
#     str_delete = domino_boletus + str_scale + "COMMIT; " 
#     db.execute(str_delete)
    
#     return True