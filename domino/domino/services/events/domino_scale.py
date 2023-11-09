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
import json
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.config.config import settings
from domino.app import _
from fastapi.responses import FileResponse
from os import getcwd

from domino.models.events.domino_round import DominoRoundsScale
from domino.models.events.tourney import TraceLotteryManual, TraceLotteryAutomatic

from domino.schemas.events.domino_rounds import DominoManualScaleCreated, DominoAutomaticScaleCreated
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
from domino.services.enterprise.userprofile import get_one as get_one_profile
from domino.services.enterprise.auth import get_url_avatar

from domino.services.events.tourney import get_one as get_one_tourney, get_setting_tourney
from domino.services.events.player import get_lst_id_player_by_elo
from domino.services.events.domino_round import get_one as get_one_round, get_first_by_tourney, configure_rounds
from domino.services.events.domino_boletus import created_boletus_for_round

# def new_initial_automatic_round(request: Request, tourney_id:str, dominoscale: list[DominoAutomaticScaleCreated], db: Session):
#     locale = request.headers["accept-language"].split(",")[0].split("-")[0];
#     result = ResultObject() 
    
#     db_tourney = get_one_tourney(tourney_id, db=db)
#     if not db_tourney:
#         raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
#     one_status_init = get_one_status_by_name('INITIADED', db=db)
    
#     # if db_tourney.status_id != one_status_init.id:
#     #     raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
#     one_settingtourney = get_setting_tourney(db_tourney.id, db=db)
#     if not one_settingtourney:
#         raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_tourney_not_exist"))
    
#     # si el torneo ya tiene mas de una ronda no se puede hacer esto
#     str_query = "Select count(*) FROM events.domino_rounds WHERE tourney_id = '" + tourney_id + "' "
#     amount_round = db.execute(str_query).fetchone()[0]
    
#     if amount_round != 1:
#         raise HTTPException(status_code=404, detail=_(locale, "round.not_initial_round"))
    
#     str_query = "Select id FROM events.domino_rounds WHERE tourney_id = '" + tourney_id + "' and round_number = 1 "
   
#     round_id = db.execute(str_query).fetchone()
#     if not round_id:
#         raise HTTPException(status_code=404, detail=_(locale, "round.not_initial_round"))
    
#     round_id = round_id[0]
#     initial_scale_by_automatic_lottery(tourney_id, round_id, dominoscale, db_tourney.modality, db=db)
    
#     # distribuir por mesas
    
#     return result

def new_initial_automatic_round(request: Request, tourney_id:str, dominoscale: list[DominoAutomaticScaleCreated], db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 
    db_tourney, round_id = get_tourney_to_configure(locale, tourney_id, db=db)
    one_status_init = get_one_status_by_name('INITIADED', db=db)
    # if db_tourney.status_id != one_status_init.id:
    #     raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
    initial_scale_by_automatic_lottery(tourney_id, round_id, dominoscale, db_tourney.modality, db=db)
    
    configure_tables_by_round(tourney_id, round_id, db_tourney.modality, db=db)
    
    # cambiar estado del torneo y Evento a Iniciado
    db_tourney.status_id = one_status_init.id
    db_tourney.event.status_id = one_status_init.id
    
    db.commit()
    
    return result

def new_initial_manual_round(request: Request, tourney_id:str, dominoscale: list[DominoManualScaleCreated], db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 
    
    db_tourney, round_id = get_tourney_to_configure(locale, tourney_id, db=db)
    one_status_init = get_one_status_by_name('INITIADED', db=db)
    # if db_tourney.status_id != one_status_init.id:
    #     raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
    initial_scale_by_manual_lottery(tourney_id, round_id, dominoscale, db_tourney.modality, db=db)
    
    configure_tables_by_round(tourney_id, round_id, db_tourney.modality, db=db)
    
    # cambiar estado del torneo a Iniciado
    db_tourney.status_id = one_status_init.id
    db_tourney.event.status_id = one_status_init.id
    
    db.commit()
    
    return result

def configure_tables_by_round(tourney_id:str, round_id: str, modality:str, db: Session):
    
    # update_elo_initial_scale(tourney_id, round_id, modality, db=db)
    
    #configurar parejas y rondas
    configure_rounds(tourney_id=tourney_id, round_id=round_id, modality=modality, db=db)
    
    #ubicar por mesas las parejas
    created_boletus_for_round(tourney_id=tourney_id, round_id=round_id, db=db)
    
    #crear las notificaciones a los jugadores con las parejas
    
    return True

def get_tourney_to_configure(locale, tourney_id:str, db: Session):
    
    db_tourney = get_one_tourney(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    one_settingtourney = get_setting_tourney(db_tourney.id, db=db)
    if not one_settingtourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_tourney_not_exist"))
    
    # si el torneo ya tiene mas de una ronda no se puede hacer esto
    str_query = "Select count(*) FROM events.domino_rounds WHERE tourney_id = '" + tourney_id + "' "
    amount_round = db.execute(str_query).fetchone()[0]
    if amount_round != 1:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_initial_round"))
    
    str_query = "Select id FROM events.domino_rounds WHERE tourney_id = '" + tourney_id + "' and round_number = 1 "
    round_id = db.execute(str_query).fetchone()
    if not round_id:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_initial_round"))
    
    return db_tourney, round_id[0]

def update_elo_initial_scale(tourney_id: str, round_id: str, modality:str, db: Session ):
    
    str_scale = "Select player_id from events.domino_rounds_scale where tourney_id = '" + tourney_id + "' " +\
        "and round_id = '" + round_id + "' order by position_number ASC "
    
    lst_scale = db.execute(str_scale).fetchall()
    
    str_select = "Select Round(SUM(elo)/2,4) as elo " if modality == 'Parejas' else 'Select elo '
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

def create_one_scale(tourney_id: str, round_id: str, round_number, position_number: int, player_id: str, db: Session ):
    one_scale = DominoRoundsScale(id=str(uuid.uuid4()), tourney_id=tourney_id, round_id=round_id, round_number=round_number, 
                                  position_number=int(position_number), player_id=player_id, is_active=True)
    db.add(one_scale)
        
    return True

def create_one_manual_trace(tourney_id: str, modality:str, position_number: int, player_id: str, db: Session ):
    
    one_trace = TraceLotteryManual(id=str(uuid.uuid4()), tourney_id=tourney_id, modality=modality, 
                                   position_number=int(position_number), player_id=player_id, is_active=True)
    db.add(one_trace)
        
    return True

def create_one_automatic_trace(tourney_id: str, modality:str, title:str, position_number:int, elo_min: float, elo_max: float, 
                               db: Session):
    one_trace = TraceLotteryAutomatic(id=str(uuid.uuid4()), tourney_id=tourney_id, modality=modality, title=title,
                                      position_number=int(position_number), elo_min=elo_min, elo_max=elo_max, 
                                      is_active=True)
    db.add(one_trace)
        
    return True
      
def initial_scale_by_manual_lottery(tourney_id: str, round_id: str, dominoscale:list, modality:str, db: Session):
    
    for item in dominoscale:
        create_one_manual_trace(tourney_id, modality, int(item.number), item.id, db=db)
        create_one_scale(tourney_id, round_id, 1, int(item.number), item.id, db=db)
    db.commit()
    return True

def initial_scale_by_automatic_lottery(tourney_id: str, round_id: str, dominoscale:list, modality:str, db: Session):
    
    position_number = 0
    for item in dominoscale:
        create_one_automatic_trace(tourney_id, modality, item.title, int(item.id), float(item.min), float(item.max), db=db)
        position_number=created_automatic_lottery(
            tourney_id, modality, round_id, float(item.min), float(item.max), position_number=position_number, db=db)
        db.commit()
    return True

def created_automatic_lottery(tourney_id: str, modality:str, round_id: str, elo_min:float, elo_max:float, position_number:int, db: Session):
    
    list_player = get_lst_id_player_by_elo(tourney_id, modality, min_elo=elo_min, max_elo=elo_max, db=db)
    
    lst_groups = sorted(list_player, key=lambda y:random.randint(0, len(list_player)))
    for item_pos in lst_groups:
        position_number += 1
        create_one_scale(tourney_id, round_id, 1, position_number, item_pos, db=db)
        db.commit()
    return position_number

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
        round_id = get_first_by_tourney(tourney_id, db=db)
    
    return get_all_players_by_tables_and_rounds(request, page, per_page=per_page, tourney_id=tourney_id, round_id=round_id, db=db)
        
def get_all_players_by_tables_and_round(request:Request, page: int, per_page: int, round_id: str, db: Session):  
    
    db_round = get_one_round(round_id, db=db)
    
    return get_all_players_by_tables_and_rounds(request, page, per_page=per_page, tourney_id=db_round.tourney_id, round_id=round_id, db=db)
    
def get_all_players_by_tables_and_rounds(request:Request, page: int, per_page: int, tourney_id: str, round_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    str_from = "FROM events.domino_boletus bol " +\
        "JOIN events.domino_tables dtab ON dtab.id = bol.table_id " +\
        "JOIN events.setting_tourney stou ON stou.tourney_id = dtab.tourney_id " 
    
    str_count = "Select count(*) " + str_from
    str_query = "SELECT DISTINCT dtab.id as table_id, dtab.table_number, is_smart, dtab.image as table_image, " +\
        "stou.image as tourney_image, bol.id as boletus_id, dtab.tourney_id " + str_from
        
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
        
        if item['table_image']:
            table_image = api_uri + "/api/advertising/" + str(item['table_id']) + "/" + item['table_image']
        else:
            if item['tourney_image']:
                table_image = api_uri + "/api/advertising/" + str(item['tourney_id']) + "/" + item['tourney_image']
            else:
                table_image = api_uri + "/api/advertising/smartdomino.png" # poner "/smartdomino.png"
                
        dict_tables = {'id': id, 'number': int(item['table_number']), 'table_id': item.table_id,
                       'type': "Inteligente" if item['is_smart'] else "Tradicional",
                       'image': table_image}
        
        dict_tables=create_dict_position(dict_tables, item.boletus_id, api_uri, db=db)
        lst_tables.append(dict_tables)
        id+=1
        
    result.data = lst_tables        
            
    return result

def get_all_pairs(request:Request, page: int, per_page: int, round_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    str_from = "FROM events.domino_boletus bol " +\
        "JOIN events.domino_tables dtab ON dtab.id = bol.table_id " +\
        "JOIN events.setting_tourney stou ON stou.tourney_id = dtab.tourney_id " 
    
    str_count = "Select count(*) " + str_from
    str_query = "SELECT DISTINCT dtab.id as table_id, dtab.table_number, is_smart, dtab.image as table_image, " +\
        "stou.image as tourney_image, bol.id as boletus_id, dtab.tourney_id " + str_from
        
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
        
        if item['table_image']:
            table_image = api_uri + "/api/advertising/" + str(item['table_id']) + "/" + item['table_image']
        else:
            if item['tourney_image']:
                table_image = api_uri + "/api/advertising/" + str(item['tourney_id']) + "/" + item['tourney_image']
            else:
                table_image = api_uri + "/api/advertising/smartdomino.png" # poner "/smartdomino.png"
                
        dict_tables = {'id': id, 'number': int(item['table_number']), 'table_id': item.table_id,
                       'type': "Inteligente" if item['is_smart'] else "Tradicional",
                       'image': table_image}
        
        dict_tables=create_dict_position(dict_tables, item.boletus_id, api_uri, db=db)
        lst_tables.append(dict_tables)
        id+=1
        
    result.data = lst_tables        
            
    return result

def create_dict_position(dict_tables, boletus_id: str, api_uri:str, db: Session):
    
    str_pos = "SELECT bpos.position_id, pro.name as profile_name, psin.elo, psin.ranking, psin.level, " +\
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
