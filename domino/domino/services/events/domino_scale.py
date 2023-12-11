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

from domino.services.events.player import get_lst_id_player_by_elo
from domino.services.events.domino_round import get_one as get_one_round, get_first_by_tourney, configure_rounds
from domino.services.events.domino_boletus import created_boletus_for_round
from domino.services.enterprise.auth import get_url_advertising

    
def new_initial_manual_round(request: Request, tourney_id:str, dominoscale: list[DominoManualScaleCreated], db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 
    
    round_id, modality = get_round_to_configure(locale, tourney_id, db=db)
    one_status_init = get_one_status_by_name('INITIADED', db=db)
    
    initial_scale_by_manual_lottery(tourney_id, round_id, dominoscale, modality, db=db)
    
    configure_tables_by_round(tourney_id, round_id, modality, db=db)
    
    # cambiar estado del torneo a Iniciado
    str_update = "UPDATE events.tourney SET status_id=" + str(one_status_init.id) + " WHERE id = '" + tourney_id + "';"
    str_update += "UPDATE events.events SET status_id=" + str(one_status_init.id) + " WHERE id IN " +\
        "(Select tourney.event_id FROM events.tourney where id = '" + tourney_id + "');COMMIT;"
    db.execute(str_update)
    
    return result

def configure_tables_by_round(tourney_id:str, round_id: str, modality:str, db: Session):
    
    update_elo_initial_scale(tourney_id, round_id, modality, db=db)
    
    #configurar parejas y rondas
    configure_rounds(tourney_id=tourney_id, round_id=round_id, modality=modality, db=db)
    
    #ubicar por mesas las parejas
    created_boletus_for_round(tourney_id=tourney_id, round_id=round_id, db=db)
    
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

def create_one_scale(tourney_id: str, round_id: str, round_number, position_number: int, player_id: str, category_id:str, db: Session ):
    one_scale = DominoRoundsScale(id=str(uuid.uuid4()), tourney_id=tourney_id, round_id=round_id, round_number=round_number, 
                                  position_number=int(position_number), player_id=player_id, is_active=True, category_id=category_id)
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


def configure_automatic_lottery(db_tourney, db_round, one_status_init, db: Session):
    
    # buscar las categorias definidas. 
    str_query = "SELECT * FROM events.domino_categories where tourney_id = '" + db_tourney.id + "' ORDER BY position_number"
    lst_categories = db.execute(str_query).fetchall()
    
    position_number=0
    for item_cat in lst_categories:   
        position_number=created_automatic_lottery(
            db_tourney.id, db_tourney.modality, db_round.id, item_cat.elo_min, item_cat.elo_max, position_number, item_cat.id, db=db)
        
    configure_tables_by_round(db_tourney.id, db_round.id, db_tourney.modality, db=db)
    
    db_tourney.status_id = one_status_init.id
    db_tourney.event.status_id = one_status_init.id
    
    db.commit()
    
    return True

def created_automatic_lottery(tourney_id: str, modality:str, round_id: str, elo_min:float, elo_max:float, position_number:int, category_id, db: Session):
    
    list_player = get_lst_id_player_by_elo(tourney_id, modality, min_elo=elo_min, max_elo=elo_max, db=db)
    
    lst_groups = sorted(list_player, key=lambda y:random.randint(0, len(list_player)))
    for item_pos in lst_groups:
        position_number += 1
        create_one_scale(tourney_id, round_id, 1, position_number, item_pos, category_id, db=db)
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
        
        table_image = get_url_advertising(tourney_id, item['table_image'] if item['table_image'] else item['tourney_image'], api_uri=api_uri)
        
        dict_tables = {'id': id, 'number': int(item['table_number']), 'table_id': item.table_id,
                       'type': "Inteligente" if item['is_smart'] else "Tradicional",
                       'image': table_image}
        
        dict_tables=create_dict_position(dict_tables, item.boletus_id, api_uri, db=db)
        lst_tables.append(dict_tables)
        id+=1
        
    result.data = lst_tables        
            
    return result

def get_all_scale_by_round(request:Request, page: int, per_page: int, round_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    str_from = "FROM events.domino_rounds_scale rsca " +\
        "JOIN events.players players ON players.id = rsca.player_id " +\
        "JOIN enterprise.profile_member mmb ON players.profile_id = mmb.id " +\
        "left join resources.city ON city.id = mmb.city_id " +\
        "left join resources.country ON country.id = city.country_id " 
    
    str_count = "Select count(*) " + str_from
    str_query = "SELECT players.id player_id, mmb.id profile_id, mmb.name profile_name, mmb.photo, rsca.position_number, " +\
        "city.name as city_name, country.name as country_name, rsca.elo, rsca.elo_variable, rsca.games_played, " +\
        "rsca.games_won, rsca.games_lost, rsca.points_positive, rsca.points_negative, rsca.points_difference " + str_from
        
    str_where = "WHERE rsca.is_active is True AND rsca.round_id = '" + round_id + "' "
        
    str_count += str_where
    str_query += str_where + " ORDER BY rsca.position_number "

    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_scale(item, db=db, api_uri=api_uri) for item in lst_data]
    
    return result

def create_dict_row_scale(item, db: Session, api_uri):
    
    photo = get_url_avatar(item['profile_id'], item['photo'], api_uri=api_uri)
    
    new_row = {'id': item['player_id'], 'name': item['profile_name'], 
               'position_number': item['position_number'],
               'country': item['country_name'] if item['country_name'] else '', 
               'city_name': item['city_name'] if item['city_name'] else '',  
               'photo' : photo, 'elo': item['elo'] if item['elo'] else 0, 
               'elo_variable': item['elo_variable'] if item['elo_variable'] else 0, 
               'games_played': item['games_played'] if item['games_played'] else 0, 
               'games_won': item['games_won'] if item['games_won'] else 0,
               'games_lost': item['games_lost'] if item['games_lost'] else 0, 
               'points_positive': item['points_positive'] if item['points_positive'] else 0,
               'points_negative': item['points_negative'] if item['points_negative'] else 0, 
               'points_difference': item['points_difference'] if item['points_difference'] else 0}
    
    return new_row

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

def get_all_tables_by_round(request:Request, page: int, per_page: int, round_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    lst_data = []
    lst_data.append({'round_number': '1', 'table_number': '1', 'table_type': 'Tradicional', 'status_partida': 'Terminada',
                     'pair_one' : {'name': 'pareja Juan - Pepe', 'player_one': 'Juan', 'player_two': 'Pepe',
                                   'avatar_one': 'jug 1', 'avatar_two': 'jug 2',
                                   'elo_one': '1600.00', 'elo_two': '1700.00',
                                   'positive_point': '60', 'negative_point': '200', 'difference_point': '-140'},
                     'pair_two' : {'name': 'pareja Jorge - Joaquin', 'player_one': 'Jorge', 'player_two': 'Joaquin',
                                   'avatar_one': 'jug 1', 'avatar_two': 'jug 2',
                                   'elo_one': '1800.00', 'elo_two': '1700.00',
                                   'positive_point': '200', 'negative_point': '60', 'difference_point': '140'}})
    
    
    result.data = lst_data
    
    return result

    api_uri = str(settings.api_uri)
    
    
    str_from = "FROM events.domino_rounds_scale rsca " +\
        "JOIN events.players players ON players.id = rsca.player_id " +\
        "JOIN enterprise.profile_member mmb ON players.profile_id = mmb.id " +\
        "left join resources.city ON city.id = mmb.city_id " +\
        "left join resources.country ON country.id = city.country_id " 
    
    str_count = "Select count(*) " + str_from
    str_query = "SELECT players.id player_id, mmb.id profile_id, mmb.name profile_name, mmb.photo, rsca.position_number, " +\
        "city.name as city_name, country.name as country_name, rsca.elo, rsca.elo_variable, rsca.games_played, " +\
        "rsca.games_won, rsca.games_lost, rsca.points_positive, rsca.points_negative, rsca.points_difference " + str_from
        
    str_where = "WHERE rsca.is_active is True AND rsca.round_id = '" + round_id + "' "
        
    str_count += str_where
    str_query += str_where + " ORDER BY rsca.position_number "

    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_scale(item, db=db, api_uri=api_uri) for item in lst_data]
    
    return result