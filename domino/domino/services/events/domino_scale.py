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
    
    return result

def configure_tables_by_round(tourney_id:str, round_id: str, modality:str, db: Session):
    
    update_elo_initial_scale(tourney_id, round_id, modality, db=db)
    # distribuir por mesas
    
    #configurar parejas y rondas
    configure_rounds(tourney_id=tourney_id, round_id=round_id, modality=modality, db=db)
    
    #ubicar por mesas las parejas
    created_boletus_for_round(tourney_id=tourney_id, round_id=round_id, db=db)
    
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
    
    # ya esto no me hace falta porque me hice un metdo que me da los jugadores en ese rango
    # lst_groups = []
    # dict_groups = {}
    # for item in dominoscale:
    #     if item.number not in dict_groups:
    #         dict_groups[item.number] = []
    #     dict_groups[item.number].append(item.id)    
    
    # posicion = 0
    # for item_g in dict_groups.values():
    #     lst_groups = sorted(item_g, key=lambda y:random.randint(0, len(item_g)))
    #     for item_pos in lst_groups:
    #         posicion += 1
    #         create_one_scale(tourney_id, round_id, 1, posicion, item_pos, db=db)
            
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
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    if not round_id:
        round_id = get_first_by_tourney(tourney_id, db=db)
    
    str_from = "FROM events.domino_boletus bol " +\
        "JOIN events.domino_tables dtab ON dtab.id = bol.table_id " +\
        "JOIN events.setting_tourney stou ON stou.tourney_id = dtab.tourney_id " 
    
    str_count = "Select count(*) " + str_from
    str_query = "SELECT DISTINCT dtab.id as table_id, dtab.table_number, is_smart, dtab.image as table_image, " +\
        "stou.image as tourney_image, bol.id as boletus_id " + str_from
        
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
    
    dict_tables = {}
    id=0
    for item in lst_data:
        if item['table_number'] not in dict_tables:
            table_image = item['table_image'] if item['table_image'] else item['tourney_image'] # mesa tiene imagen asociada
            
            dict_tables[item['table_number']] = {'id': id, 'number': int(item['table_number']), 
                                                 'type': "Inteligente" if item['is_smart'] else "Tradicional",
                                                 'image': table_image}
            dict_tables[item['table_number']] = create_dict_position(item.boletus_id, api_uri, db=db)
        id+=1
    print('tables')
    print(dict_tables)
    result.data = dict_tables        
            
    # playerOne: {id: "1", name: "Juán Carlos", elo: 15235, nivel: "Experto", index: 1, avatar: "/profile/user-vector.jpg"},
    #   playerTwo: {id: "2", name: "Ricardo", elo: 15226, nivel: "Experto", index: 2, avatar: "/profile/user-vector.jpg"},
    #   playerThree: {id: "3", name: "Migue", elo: 14230, nivel: "Experto", index: 3, avatar: "/profile/user-vector.jpg"},
    #   playerFour: {id: "4", name: "Jesús", elo: 12345, nivel: "Profesional", index: 4, avatar: "/profile/user-vector.jpg"},
    
    # result.data = [create_dict_row(item, tourney_id, page, db=db, api_uri=api_uri) for item in lst_data]
    
    {
      id: 0,
      number: 1,
      type: "Inteligente",
      image: "/smartdomino.png",
      playerOne: {id: "1", name: "Juán Carlos", elo: 15235, nivel: "Experto", index: 1, avatar: "/profile/user-vector.jpg"},
      playerTwo: {id: "2", name: "Ricardo", elo: 15226, nivel: "Experto", index: 2, avatar: "/profile/user-vector.jpg"},
      playerThree: {id: "3", name: "Migue", elo: 14230, nivel: "Experto", index: 3, avatar: "/profile/user-vector.jpg"},
      playerFour: {id: "4", name: "Jesús", elo: 12345, nivel: "Profesional", index: 4, avatar: "/profile/user-vector.jpg"},
    },
    
    da = {1: {'playerOne': {'id': 1, 'name': 'usuario.tres', 'elo': Decimal('2504.2500'), 
                            'nivel': 'Avanzado', 'index': None, 
                            'avatar': 'http://127.0.0.1:5000/api/avatar/dbc1c718-e9a0-4a8b-8c82-4352e566283f/dbc1c718-e9a0-4a8b-8c82-4352e566283f.jpg'}, 
              'playerTwo': {'id': 2, 'name': 'usuario.seis_a', 'elo': Decimal('2004.7500'), 
                            'nivel': 'Experto', 'index': None, 
                            'avatar': 'http://127.0.0.1:5000/api/avatar/08f41160-0787-43ec-811f-17892b849577/08f41160-0787-43ec-811f-17892b849577.jpg'}, 
              'playerThree': {'id': 3, 'name': 'wilfre', 'elo': Decimal('2571.7500'), 
                              'nivel': 'Experto', 'index': None, 
                              'avatar': 'http://127.0.0.1:5000/api/avatar/93b33904-6635-47de-bf7e-74f461dabb2e/93b33904-6635-47de-bf7e-74f461dabb2e.jpg'}, 
              'playerFour': {'id': 4, 'name': 'usuario.uno_b', 'elo': Decimal('2382.7500'), 
                             'nivel': 'Avanzado', 'index': None, 
                             'avatar': 'http://127.0.0.1:5000/api/avatar/0178891e-7a7a-4d74-a649-e561622adc04/0178891e-7a7a-4d74-a649-e561622adc04.jpg'}}, 
          2: {}, 
          3: {'playerOne': {'id': 1, 'name': 'usuario.siete_o', 'elo': Decimal('2207.2500'), 'nivel': 'Intermedio', 'index': None, 'avatar': 'http://127.0.0.1:5000/api/avatar/3efb1198-258a-49e3-834f-6f214685ed42/3efb1198-258a-49e3-834f-6f214685ed42.jpg'}, 'playerTwo': {'id': 2, 'name': 'richard', 'elo': Decimal('2652.7500'), 'nivel': 'Avanzado', 'index': None, 'avatar': 'http://127.0.0.1:5000/api/avatar/2693afbe-50ef-4deb-927f-c323efaf9dc7/2693afbe-50ef-4deb-927f-c323efaf9dc7.jpg'}, 'playerThree': {'id': 3, 'name': 'usuario.cinco', 'elo': Decimal('2490.7500'), 'nivel': 'Intermedio', 'index': None, 'avatar': 'http://127.0.0.1:5000/api/avatar/7a6a318f-e37b-44f2-ae71-7ac17390a488/7a6a318f-e37b-44f2-ae71-7ac17390a488.jpg'}, 'playerFour': {'id': 4, 'name': 'usuario.dos_a', 'elo': Decimal('2031.7500'), 'nivel': 'Experto', 'index': None, 'avatar': 'http://127.0.0.1:5000/api/avatar/9030ce88-8088-4e69-8d9e-be90e96b20b3/9030ce88-8088-4e69-8d9e-be90e96b20b3.jpg'}}}
    
    return result

def create_dict_position(boletus_id: str, api_uri:str, db: Session):
    
    str_pos = "SELECT bpos.position_id, pro.name as profile_name, psin.elo, psin.ranking, psin.level, " +\
        "bpos.single_profile_id, pro.photo, bpos.scale_number " +\
        "FROM events.domino_boletus_position bpos " +\
        "JOIN enterprise.profile_single_player psin ON psin.profile_id = bpos.single_profile_id " +\
        "JOIN enterprise.profile_member pro ON pro.id = psin.profile_id " +\
        "WHERE bpos.boletus_id = '" + boletus_id + "' ORDER BY bpos.position_id "
    lst_data = db.execute(str_pos)
    
    dicc_pos = {}
    for item in lst_data:
        photo = get_url_avatar(item['single_profile_id'], item['photo'], api_uri=api_uri)
        dict_player = {'id': item.position_id, 'name': item.profile_name, 'elo': item.elo, 'nivel': item.level, 
                       'index': item.scale_number, 'avatar': photo}
        
        if item.position_id == 1:
            dicc_pos['playerOne'] = dict_player
        elif item.position_id == 2:  
            dicc_pos['playerTwo'] = dict_player
        elif item.position_id == 3:
            dicc_pos['playerThree'] = dict_player
        elif item.position_id == 4:  
            dicc_pos['playerFour'] = dict_player
    
    return dicc_pos

# def create_dict_row(item, tourney_id, page, db: Session, api_uri):
    
#     photo = get_url_avatar(item['single_profile_id'], item['photo'], api_uri=api_uri)
        
    
#     # new_row = {'id': int(item['table_number']), 
#     #            'position_id': item['position_id'], 'table_id': item['table_id'], 
#     #            'table_number': item['table_number'], 'is_smart': item['is_smart'],  
#     #            'amount_bonus': item['amount_bonus'], 'table_image': table_image,  
#     #            'country': item['country_name'], 'city_name': item['city_name'],  
#     #            'photo' : photo, 'elo': item['elo'], 'ranking': item['ranking'], 'level': item['level']}
    
    
#     # {
#     #   id: 0,
#     #   number: 1,
#     #   type: "Inteligente",
#     #   image: "/smartdomino.png",
#     #   playerOne: {id: "1", name: "Juán Carlos", elo: 15235, nivel: "Experto", index: 1, avatar: "/profile/user-vector.jpg"},
#     #   playerTwo: {id: "2", name: "Ricardo", elo: 15226, nivel: "Experto", index: 2, avatar: "/profile/user-vector.jpg"},
#     #   playerThree: {id: "3", name: "Migue", elo: 14230, nivel: "Experto", index: 3, avatar: "/profile/user-vector.jpg"},
#     #   playerFour: {id: "4", name: "Jesús", elo: 12345, nivel: "Profesional", index: 4, avatar: "/profile/user-vector.jpg"},
#     # },
#     id+=1
#     return new_row

# def distribute_all_player(request:Request, tourney_id:str, round_id:str, db: Session):
#     locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
#     db_tourney = get_one_tourney(tourney_id, db=db)
#     if not db_tourney:
#         raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
#     round_initial = get_one_round(round_id, db=db)
#     if not round_initial:
#         raise HTTPException(status_code=404, detail=_(locale, "dominoround.not_found"))
    
#     configure_rounds(db_tourney.id, round_initial.id, db_tourney.modality, db=db)
    
    # return True