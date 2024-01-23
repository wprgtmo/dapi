import math
import uuid

from datetime import datetime
from fastapi import HTTPException, Request, UploadFile, File
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import and_
from passlib.context import CryptContext
import json
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.config.config import settings
from domino.app import _
from fastapi.responses import FileResponse
from os import getcwd

from domino.models.events.domino_round import DominoRounds, DominoRoundsPairs, DominoRoundsScale

from domino.schemas.resources.result_object import ResultObject
from domino.schemas.events.domino_rounds import DominoRoundsCreated

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
from domino.services.enterprise.users import get_one_by_username
from domino.services.enterprise.userprofile import get_one as get_one_profile
from domino.services.events.domino_boletus import calculate_amount_tables_playing
from domino.services.events.tourney import get_one as get_tourney_by_id, calculate_amount_tables, calculate_amount_categories, \
    calculate_amount_players_playing, calculate_amount_players_by_status, get_lst_categories_of_tourney, reconfig_amount_tables
from domino.services.events.calculation_serv import calculate_score_expected
                         
def get_all(request:Request, tourney_id:str, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session,
            only_initiaded=False):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    # verificar que el perfil sea admon del evento al cual pertenece el torneo.
    # db_member_profile = get_one_profile(id=profile_id, db=db)
    # if not db_member_profile:
    #     raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
   
    # if db_member_profile.profile_type != 'EVENTADMON':
    #     raise HTTPException(status_code=400, detail=_(locale, "userprofile.user_not_event_admon"))
    
    str_from = "FROM events.domino_rounds drounds " +\
        "JOIN events.tourney dtou ON dtou.id = drounds.tourney_id " +\
        "JOIN resources.entities_status sta ON sta.id = drounds.status_id " 
        
    str_count = "Select count(*) " + str_from
    str_query = "Select drounds.id, round_number, drounds.summary, drounds.start_date, drounds.close_date, " + \
        "sta.name as status_name, sta.description as status_description " + str_from
    
    str_where = " WHERE drounds.tourney_id = '" + tourney_id + "' "  
    
    dict_query = {'round_number': " AND round_number = " + criteria_value}
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if only_initiaded:
        str_where += "AND sta.name != 'CREATED' "
          
    str_count += str_where
    str_query += str_where
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY round_number ASC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item) for item in lst_data]
    
    return result

def create_dict_row(item, amount_tables=0, amount_pairs=0):
    
    new_row = {'id': item['id'], 'round_number': item['round_number'], 
               'summary': item['summary'], 'start_date': item['start_date'].strftime('%d-%m-%Y'),
               'status_name': item['status_name'], 'status_description': item['status_description'], 
               'close_date': item['close_date'].strftime('%d-%m-%Y') if str(item['status_name']) == 'FINALIZED' else ''}
    
    if amount_tables:
        new_row['amount_tables'] = amount_tables
        new_row['amount_pairs'] = amount_pairs
        
    return new_row

def get_one(round_id: str, db: Session):  
    return db.query(DominoRounds).filter(DominoRounds.id == round_id).first()

def get_one_by_number(round_number: int, db: Session): 
    # status_canceled = get_one_status_by_name('CANCELLED', db=db) 
    # return db.query(DominoRounds).filter(and_(DominoRounds.round_number==round_number).\
    #     filter(DominoRounds.status_id != status_canceled.id)).first()
    
    return db.query(DominoRounds).filter_by(round_number=round_number).first()

def get_one_by_id(round_id: str, db: Session): 
    result = ResultObject()  
    
    one_round = get_one(round_id, db=db)
    if not one_round:
        raise HTTPException(status_code=404, detail="round.not_found")
    
    str_query = "Select drounds.id, round_number, drounds.summary, drounds.start_date, drounds.close_date, " +\
        "sta.name as status_name, sta.description as status_description " +\
        "FROM events.domino_rounds drounds " +\
        "JOIN events.tourney dtou ON dtou.id = drounds.tourney_id " +\
        "JOIN resources.entities_status sta ON sta.id = drounds.status_id " +\
        " WHERE drounds.id = '" + round_id + "' "  
        
    lst_data = db.execute(str_query) 
    
    str_amount_tables = "Select count(*) from events.domino_boletus where round_id = '" + str(round_id) + "' "
    amount_tables = db.execute(str_amount_tables).fetchone()[0]
    
    str_amount_pairs = "Select count(*) from events.domino_rounds_pairs where round_id = '" + str(round_id) + "' "
    amount_pairs=db.execute(str_amount_pairs).fetchone()[0]
    
    for item in lst_data:
        result.data = create_dict_row(item, amount_tables=amount_tables, amount_pairs=amount_pairs)
        
    if not result.data:
        raise HTTPException(status_code=404, detail="round.not_found")
    
    return result

def get_first_by_tourney(tourney_id: str, db: Session): 
    status_canceled = get_one_status_by_name('CANCELLED', db=db) 
    return db.query(DominoRounds).filter(DominoRounds.tourney_id==tourney_id).\
        filter(DominoRounds.status_id != status_canceled.id).order_by(DominoRounds.round_number.asc()).first()
        
def get_last_by_tourney(tourney_id: str, db: Session): 
    status_canceled = get_one_status_by_name('CANCELLED', db=db) 
    return db.query(DominoRounds).filter(DominoRounds.tourney_id==tourney_id).\
        filter(DominoRounds.status_id != status_canceled.id).order_by(DominoRounds.round_number.desc()).first()
    
def created_round_default(db_tourney, summary:str, db:Session, round_number:int , is_first=False, is_last=False):
 
    # buscar por el numero de ronda si existe, no hacer nada, ya esta creada.
    str_number = "SELECT id FROM events.domino_rounds where tourney_id = '" + db_tourney.id + "' " +\
        "AND round_number = '" + str(round_number) + "' "
    last_number = db.execute(str_number).fetchone()
        
    if last_number:
        return True
    
    status_creat = get_one_status_by_name('CREATED', db=db)
    
    db_round = DominoRounds(
        id=str(uuid.uuid4()), tourney_id=db_tourney.id, round_number=round_number, summary=summary, start_date=datetime.now(), 
        close_date=datetime.now(), created_by=db_tourney.updated_by, updated_by=db_tourney.updated_by, created_date=datetime.now(), 
        updated_date=datetime.now(), status_id=status_creat.id, is_first=is_first, is_last=is_last)
    
    try:
        db.add(db_round)
        db.commit()
        return db_round
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return None

def configure_next_rounds(db_round, db:Session):
 
    round_number = db_round.round_number + 1
    summary = 'Ronda Nro. ' + str(round_number)
    
    dict_order = {'JG': 'games_won DESC',
                  'ERA': 'elo_current DESC',
                  'DP': 'points_difference DESC'}
    
    status_config = get_one_status_by_name('CONFIGURATED', db=db)
    db_round_next = DominoRounds(
        id=str(uuid.uuid4()), tourney_id=db_round.tourney_id, round_number=round_number, summary=summary, start_date=datetime.now(), 
        close_date=datetime.now(), created_by=db_round.updated_by, updated_by=db_round.updated_by, created_date=datetime.now(), 
        updated_date=datetime.now(), status_id=status_config.id, is_first=False, is_last=False)
    
    # calcular en base a los jugadores la cantidad de mesas que necesito y crearlas
    amount_tables, amount_player_waiting = reconfig_amount_tables(db_round.tourney, db=db)
    
    # ordenar la escala actual por los criterior de ordenamiento del torneo.
    str_list_player = "Select puse.*, sta.name as status_name, category_id from events.players_users puse " +\
        "join events.players play ON play.id = puse.player_id join resources.entities_status sta ON sta.id = play.status_id " +\
        "Where sta.name IN ('CONFIRMED', 'PLAYING', 'WAITING') and tourney_id = '" + db_round.tourney.id + "' " 
    
    # si usa segmentacion, incluir la categoria como primer criterio para ordenar y mantener
    # ver despues como lo hago
    if db_round.tourney.use_segmentation:
        str_order_by = " ORDER BY category_number ASC, " + dict_order[db_round.tourney.round_ordering_one]
    else:
        str_order_by = " ORDER BY " + dict_order[db_round.tourney.round_ordering_one]
    
    if db_round.tourney.round_ordering_two:
        str_order_by += ", " + dict_order[db_round.tourney.round_ordering_two]
    if db_round.tourney.round_ordering_three:
        str_order_by += ", " + dict_order[db_round.tourney.round_ordering_three]
        
    str_list_player += str_order_by
    lst_all_player_to_order = db.execute(str_list_player).fetchall()
    
    lst_player_to_order, dict_play, position_number, lst_play_waiting =  [], {}, 0, []
    
    for item_pos in lst_all_player_to_order:
        
        new_record = create_new_record(item_pos, position_number)
        lst_player_to_order.append(new_record)
        dict_play[position_number] = new_record
        
        num_table = divmod(int(position_number + 1),4)
        if num_table[0] > amount_tables:
            if new_record['status_name'] == 'WAITING':
                lst_play_waiting.append(new_record)
        else:
            if num_table[0] == amount_tables and num_table[1] != 0:
                if new_record['status_name'] == 'WAITING':
                    lst_play_waiting.append(new_record)
                
        position_number += 1
    
    if amount_player_waiting != 0:  # coinciden mesas y jugadores, es solo ordernar.
        
        last_position_play = position_number -1 
        for item_waiting in lst_play_waiting:
            for item_play in dict_play:
                if dict_play[last_position_play]['status_name'] == 'PLAYING':
                    lst_player_to_order[last_position_play], lst_player_to_order[item_waiting['position_number']] = lst_player_to_order[item_waiting['position_number']], lst_player_to_order[last_position_play]
                    last_position_play -= 1
                    break
                else:
                    last_position_play -= 1
        
    # recorrer la nueva lista y ponerla ya en la escala
    position_number = 1
    for item_scala in lst_player_to_order:
        one_scale = DominoRoundsScale(
            id=str(uuid.uuid4()), tourney_id=db_round.tourney.id, round_id=db_round_next.id, round_number=db_round_next.round_number, 
            position_number=int(position_number), player_id=item_scala['player_id'], is_active=True, category_id=item_scala['category_id'],
            elo=item_scala['elo'], elo_variable=item_scala['elo_current'], games_played=item_scala['games_played'], 
            games_won=item_scala['games_won'], games_lost=item_scala['games_lost'], points_positive=item_scala['points_positive'], 
            points_negative=item_scala['points_negative'], points_difference=item_scala['points_difference'], 
            score_expected=item_scala['score_expected'], score_obtained=item_scala['score_obtained'],
            acumulated_games_played=item_scala['games_played'], k_value=item_scala['k_value'], 
            elo_at_end=item_scala['elo_at_end'], bonus_points=item_scala['bonus_points'])
        
        db.add(one_scale)
        position_number += 1
    
    try:
        db.add(db_round_next)
        db.commit()
        return db_round_next
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return None

def create_new_record(item, position_number):
    return {'position_number': position_number, 'player_id': item.player_id, 'profile_id': item.profile_id,
            'level': item.level, 'elo': item.elo, 'elo_current': item.elo_current, 'elo_at_end': item.elo_at_end,
            'games_played': item.games_played, 'games_won': item.games_won, 'games_lost': item.games_lost, 
            'points_positive': item.points_positive, 'points_negative': item.points_negative, 
            'points_difference': item.points_difference, 'score_expected': item.score_expected, 
            'score_obtained': item.score_obtained, 'k_value': item.k_value, 'penalty_yellow': item.penalty_yellow,
            'penalty_red': item.penalty_red, 'penalty_total': item.penalty_total, 'bonus_points': item.bonus_points,
            'status_name': item.status_name, 'category_id': item.category_id}
    
def configure_new_rounds(tourney_id, summary:str, db:Session, created_by:str, round_number=''):
 
    if round_number:
        real_round_number = round_number
    else:
        str_number = "SELECT round_number FROM events.domino_rounds where tourney_id = '" + tourney_id + "' " +\
            "ORDER BY round_number DESC LIMIT 1; "
        last_number = db.execute(str_number).fetchone()
    
        real_round_number = 1 if not last_number else int(last_number[0]) + 1
    
    status_creat = get_one_status_by_name('CREATED', db=db)
    
    id = str(uuid.uuid4())
    db_round = DominoRounds(id=id, tourney_id=tourney_id, round_number=real_round_number, summary=summary,
                            start_date=datetime.now(), close_date=datetime.now(), created_by=created_by, 
                            updated_by=created_by, created_date=datetime.now(), updated_date=datetime.now(),
                            status_id=status_creat.id)
    
    try:
        db.add(db_round)
        db.commit()
        return db_round
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return None
    
def get_info_to_aperture(request:Request, round_id:str, db:Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    db_round = get_one(round_id=round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_found"))
    
    result.data = get_obj_info_to_aperturate(db_round, db)   
     
    return result

def calculate_amount_rounds_played(tourney_id, db: Session):
    
    one_status_canceled = get_one_status_by_name('CANCELLED', db=db)
    str_count = "SELECT count(id) FROM events.domino_rounds where tourney_id = '" + str(tourney_id) + "' " +\
        "and status_id != " + str(one_status_canceled.id)
        
    count_round = db.execute(str_count).fetchone()[0]
    
    return count_round

def get_obj_info_to_aperturate(db_round, db:Session):
    
    new_round = DominoRoundsCreated(id=db_round.id)
    
    new_round.round_number = db_round.round_number
    
    new_round.amount_tables = calculate_amount_tables(db_round.tourney.id, db_round.tourney.modality, db=db)
    new_round.amount_tables_playing = calculate_amount_tables_playing(db_round.id, db=db)
    new_round.amount_categories = calculate_amount_categories(db_round.tourney.id, db=db)
    new_round.modality = db_round.tourney.modality
    
    count_round = calculate_amount_rounds_played(db_round.tourney.id, db=db)
    is_last = True if int(count_round) == int(db_round.tourney.number_rounds) else False
    
    new_round.is_first, new_round.is_last = db_round.is_first, is_last
    
    new_round.amount_players_playing = calculate_amount_players_by_status(db_round.tourney.id, "PLAYING", db=db)
    new_round.amount_players_waiting = calculate_amount_players_by_status(db_round.tourney.id, "WAITING", db=db)
    new_round.amount_players_pause = calculate_amount_players_by_status(db_round.tourney.id, "PAUSE", db=db)
    new_round.amount_players_expelled = calculate_amount_players_by_status(db_round.tourney.id, "EXPELLED", db=db)
    
    if new_round.amount_players_playing == 0:
        new_round.amount_players_playing = calculate_amount_players_playing(db_round.tourney.id, db=db)
        
    new_round.status_id, new_round.status_name = db_round.status.id, db_round.status.name
    new_round.status_description = db_round.status.description
    
    new_round.lottery_type = db_round.tourney.lottery_type
    
    new_round.use_segmentation = db_round.tourney.use_segmentation
    new_round.use_penalty = db_round.tourney.use_penalty
    new_round.use_bonus = db_round.tourney.use_bonus
    
    return new_round

# def aperture_new_round(request:Request, round_id:str, round: DominoRoundsAperture, db:Session):
#     locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
#     result = ResultObject() 
#     currentUser = get_current_user(request)
    
#     db_round = get_one(round_id=round_id, db=db)
#     if not db_round:
#         raise HTTPException(status_code=404, detail=_(locale, "round.not_found"))
    
#     one_status_created = get_one_status_by_name('CREATED', db=db)
#     if not one_status_created:
#         raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
#     if db_round.status_id != one_status_created:
#         raise HTTPException(status_code=404, detail=_(locale, "round.status_incorrect"))
    
#     info_round = get_obj_info_to_aperturate(db_round.tourney, db, locale=locale) 
    
#     # verificar que lo que viene de la interfaz coincide con lo de la base de datos
#     if info_round.amount_players_playing < 8:
#         raise HTTPException(status_code=404, detail=_(locale, "tourney.amount_player_incorrect"))
    
#     str_query = "SELECT count(tourney_id) FROM events.domino_categories where tourney_id = '" + db_round.tourney.id + "' "
#     amount = db.execute(str_query).fetchone()[0]
#     if amount == 0:
#         raise HTTPException(status_code=404, detail=_(locale, "tourney.category_not_configurated"))
    
#     if db_round.is_first:
#         # validar todas las categorias estén contempladas entre los elo de los jugadores.
#         lst_category = get_lst_categories_of_tourney(tourney_id=db_round.tourney.id, db=db)
#         if not verify_category_is_valid(float(db_round.tourney.elo_max), float(db_round.tourney.elo_min), lst_category=lst_category):
#             raise HTTPException(status_code=400, detail=_(locale, "tourney.setting_category_incorrect"))
#         if db_round.tourney.lottery_type == "MANUAL":
#             result_init = configure_automatic_lottery(db_tourney, db_round_ini, one_status_init, db=db)
# #         if not result_init:
# #             raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_initial_scale_failed"))

#         # salvar posicionamiento manual
#         # 0 crear el primer posicionamiento automático.
#     else:
#         pass
#         # crear el posiciinamiento según criterio de ordenamiento de las rondas
        
#     # distribuir parejas , mesas, etc.
    
#     # poner la ronda en estado de configurada, para que pase a ser publicada.
        

#     try:
#         configure_new_rounds(
#             tourney_id=tourney_id, summary='', db=db, created_by=currentUser['username'], round_number=info_round.round_number,
#             is_first=info_round.is_first, is_last=info_round.is_last, use_segmentation=round.use_segmentation, 
#             use_bonus=round.use_bonus, amount_bonus_tables=round.amount_bonus_tables, amount_bonus_points=round.amount_bonus_points,
#             amount_tables=info_round.amount_tables, amount_categories=info_round.amount_categories, 
#             amount_players_playing=info_round.amount_players_playing, amount_players_waiting=info_round.amount_players_waiting,
#             amount_players_pause=info_round.amount_players_pause, amount_players_expelled=info_round.amount_players_expelled)
#         return result
    
#     except (Exception, SQLAlchemyError, IntegrityError) as e:
#         raise HTTPException(status_code=404, detail=_(locale, "round.error_started_round"))

# def verify_category_is_valid(elo_max: float, elo_min: float, lst_category: list):
    
#     current_elo_max = float(elo_max)
#     current_elo_min = float(elo_min)
#     for item in lst_category:
#         if current_elo_max !=  float(item['elo_max']):
#             return False
#         else:
#             current_elo_max = float(item['elo_min']) - 1 
#             current_elo_min = float(item['elo_min'])
    
#     if current_elo_min != float(elo_min):
#         return False
    
#     return True
    
# def start_one_round(request:Request, tourney_id:str, db:Session):
#     locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
#     result = ResultObject() 
#     currentUser = get_current_user(request)
    
#     one_status_created = get_one_status_by_name('CREATED', db=db)
#     if not one_status_created:
#         raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
#     one_status_end = get_one_status_by_name('INITIADED', db=db)
#     if not one_status_end:
#         raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
#     # buscar la utima ronda abierta del torneo
#     str_number = "SELECT id FROM events.domino_rounds where tourney_id = '" + str(tourney_id) + "' " +\
#         "and status_id = " +str(one_status_created.id) + " ORDER BY round_number DESC LIMIT 1; "
       
#     last_id = db.execute(str_number).fetchone()
#     if not last_id:
#         raise HTTPException(status_code=404, detail=_(locale, "round.not_exist_created_round"))

#     round_id = last_id[0]
#     db_round = get_one(round_id, db=db)
        
#     try:
#         db_round.status_id = one_status_end.id
#         db_round.start_date = datetime.now()
#         db_round.close_date = datetime.now()
#         db_round.updated_by = currentUser['username']
#         db_round.updated_date = datetime.now()
        
#         db.add(db_round)
#         db.commit()
#         return result
    
#     except (Exception, SQLAlchemyError, IntegrityError) as e:
#         raise HTTPException(status_code=404, detail=_(locale, "round.error_started_round"))
    
def delete(request: Request, round_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_round = get_one(round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_found"))
    
    status_canc = get_one_status_by_name('CANCELLED', db=db)
        
    change_status_round(db_round, status_canc, currentUser['username'], db=db)
    
    db.commit()
    
    return result

def start_one_round(request: Request, round_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    db_round = get_one(round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_found"))
    
    status_publicted = get_one_status_by_name('PUBLICATED', db=db)
    status_init = get_one_status_by_name('INITIADED', db=db)
    
    if db_round.status_id != status_publicted.id:
        raise HTTPException(status_code=404, detail=_(locale, "round.status_incorrect"))
    
    change_status_round(db_round, status_init, currentUser['username'], db=db)
    
    # cambiar aqui el estado del torneo a iniciado
    status_init = get_one_status_by_name('INITIADED', db=db)
    db_round.tourney.status_id = status_init.id
    db_round.tourney.event.status_id = status_init.id
    
    db.add(db_round.tourney)
    db.add(db_round.tourney.event)
    
    db.commit()
    
    db_round_ini = get_one(round_id=round_id, db=db)
    result.data = get_obj_info_to_aperturate(db_round_ini, db) 
    
    return result
 
def publicate_one_round(request: Request, round_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    db_round = get_one(round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_found"))
    
    status_publicated = get_one_status_by_name('PUBLICATED', db=db)
    
    if db_round.status.name != 'CONFIGURATED':
        raise HTTPException(status_code=404, detail=_(locale, "round.status_incorrect"))
    
    change_status_round(db_round, status_publicated, currentUser['username'], db=db)
    
    # cambiar aqui el estado del torneo a iniciado
    status_init = get_one_status_by_name('INITIADED', db=db)
    db_round.tourney.status_id = status_init.id
    db_round.tourney.event.status_id = status_init.id
    
    db.add(db_round.tourney)
    db.add(db_round.tourney.event)
    
    print('cambie estado del evento')
    print('****************')
    
    db.commit()
    
    db_round_ini = get_one(round_id=round_id, db=db)
    result.data = get_obj_info_to_aperturate(db_round_ini, db) 
    
    return result

# def close_one_round(request: Request, round_id: str, open_new: bool, db: Session):
#     locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
#     result = ResultObject() 
#     currentUser = get_current_user(request) 
    
#     db_round = get_one(round_id, db=db)
#     if not db_round:
#         raise HTTPException(status_code=404, detail=_(locale, "round.not_found"))
    
#     status_init = get_one_status_by_name('FINALIZED', db=db)
    
#     if db_round.status.name != 'REVIEW':
#         raise HTTPException(status_code=404, detail=_(locale, "round.status_incorrect"))
    
#     # change_status_round(db_round, status_init, currentUser['username'], db=db)
#     if open_new:
#         configure_next_rounds(db_round, db=db)
    
#     return result

def change_status_round(db_round, status, username, db: Session):
    
    db_round.status_id = status.id
    if username:
        db_round.updated_by = username
    db_round.updated_date = datetime.now()
            
    try:
        db.add(db_round)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        return False


def create_pair_for_rounds(tourney_id: str, round_id: str, modality:str, db: Session):
    
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

def created_one_pair(tourney_id:str, round_id:str, one_player_id:str, two_player_id:str, name:str, profile_type:str,
                     created_by:str, db: Session, position_number:int, scale_number_one_player:int, 
                     scale_number_two_player:int, scale_id_one_player:str, scale_id_two_player:str,
                     player_id:str=None):
    
    one_pair = DominoRoundsPairs(id=str(uuid.uuid4()), tourney_id=tourney_id, round_id=round_id, one_player_id=one_player_id,
                                 two_player_id=two_player_id, name=name, profile_type=profile_type, player_id=player_id,
                                 position_number=position_number, 
                                 scale_number_one_player=scale_number_one_player, scale_number_two_player=scale_number_two_player,
                                 scale_id_one_player=scale_id_one_player, scale_id_two_player=scale_id_two_player,
                                 created_by=created_by, updated_by=created_by, 
                                 created_date=datetime.today(), updated_date=datetime.today(), is_active=True)
    
    db.add(one_pair)
        
    return True

def create_pair_for_profile_pair(tourney_id: str, round_id: str, db: Session, created_by: str):
    
    str_user = "Select mmb.name, puse.single_profile_id as profile_id, rsca.player_id, rsca.position_number  " +\
        "from events.domino_rounds_scale rsca " +\
        "JOIN events.players play ON play.id = rsca.player_id " +\
        "JOIN enterprise.profile_member mmb ON play.profile_id = mmb.id " +\
        "JOIN enterprise.profile_users puse ON puse.profile_id = mmb.id " +\
        "Where rsca.tourney_id = '" + tourney_id + "' AND rsca.round_id = '" + round_id + "' order by rsca.position_number ASC "
    
    lst_pair = db.execute(str_user)
    dict_pair = {}
    position_number=0
    for item in lst_pair:
        if item.name not in dict_pair:
            dict_pair[item.name] = {'player_id': item.player_id, 'scale_number': item.position_number, 'users': []}
        dict_pair[item.name]['users'].append(item.profile_id)
        
    for item_key, item_value in dict_pair.items():
        position_number+=1
        created_one_pair(tourney_id, round_id, item_value['users'][0], item_value['users'][1], item_key, 
                         'Parejas', created_by=created_by, db=db, position_number=position_number, 
                         scale_number_one_player=item_value['scale_number'], 
                         scale_number_two_player=item_value['scale_number'], player_id=item_value['player_id'])    
    return True

def create_pair_for_profile_single(tourney_id: str, round_id: str, db: Session, created_by: str):
    
    str_user = "Select mmb.name, puse.single_profile_id as profile_id, rsca.player_id, rsca.position_number, rsca.id " +\
        "from events.domino_rounds_scale rsca " +\
        "JOIN events.players play ON play.id = rsca.player_id " +\
        "JOIN enterprise.profile_member mmb ON play.profile_id = mmb.id " +\
        "JOIN enterprise.profile_users puse ON puse.profile_id = mmb.id " +\
        "Where rsca.tourney_id = '" + tourney_id + "' AND rsca.round_id = '" + round_id + "' order by rsca.position_number ASC "
    
    lst_pair = db.execute(str_user)
    lst_all_pair = []
    for item in lst_pair:
        lst_all_pair.append({'name': item.name, 'player_id': item.player_id, 
                             'profile_id': item.profile_id, 'scale_number': item.position_number,
                             'scale_id': item.id})
    
    lst_par, lst_impar, pos = [], [], 0
    for i in lst_all_pair:   
        if  pos % 2 == 0:
            lst_par.append(lst_all_pair[pos])
        else:
            lst_impar.append(lst_all_pair[pos])
        pos+=1 
    
    amount_pair_div = divmod(len(lst_all_pair),2)
    position_number=0
    
    for num in range(0, amount_pair_div[0]-1, 2):
        position_number+=1
        name = lst_par[num]['name'] + " - " + lst_par[num+1]['name']
        created_one_pair(tourney_id, round_id, lst_par[num]['profile_id'], lst_par[num+1]['profile_id'], name, 
                         'Individual', created_by=created_by, db=db, position_number=position_number, 
                         scale_number_one_player=lst_par[num]['scale_number'],
                         scale_number_two_player=lst_par[num+1]['scale_number'], 
                         scale_id_one_player=lst_par[num]['scale_id'],
                         scale_id_two_player=lst_par[num+1]['scale_id'],
                         player_id=None)
        position_number+=1
        name = lst_impar[num]['name'] + " - " + lst_impar[num+1]['name']
        created_one_pair(tourney_id, round_id, lst_impar[num]['profile_id'], lst_impar[num+1]['profile_id'], name, 
                         'Individual', created_by=created_by, db=db, position_number=position_number, 
                         scale_number_one_player=lst_impar[num]['scale_number'],
                         scale_number_two_player=lst_impar[num+1]['scale_number'], 
                         scale_id_one_player=lst_impar[num]['scale_id'],
                         scale_id_two_player=lst_impar[num+1]['scale_id'], 
                         player_id=None)

    if  amount_pair_div[1] > 0:  # parejas impar  
        created_one_pair(tourney_id, round_id, lst_par[len(lst_par)-1]['profile_id'], None, 
                         lst_par[len(lst_par)-1]['name'], 'Individual', created_by=created_by, 
                         db=db, position_number=position_number+1, 
                         scale_number_one_player=lst_par[len(lst_par)-1]['scale_number'],
                         scale_number_two_player=None, scale_id_one_player=lst_par[len(lst_par)-1]['scale_id'],
                         scale_id_two_player=None, player_id=None) 
            
    return True
    
def configure_rounds(tourney_id: str, round_id: str, modality:str, created_by:str, db: Session):

    # si la modalidad es pareja, es vaciar la tabla del escalafón.
    # si es individual, aplico el algoritmo de distribuir por mesas...
    
    if modality == 'Parejas':
        create_pair_for_profile_pair(tourney_id, round_id, db=db, created_by=created_by)
    else:
        create_pair_for_profile_single(tourney_id, round_id, db=db, created_by=created_by)
        
    db.commit()    
    
    return True 

def remove_configurate_round(tourney_id: str, round_id: str, db: Session):
    
    str_round = "WHERE round_id = '" + round_id + "'; "
    str_id_boletus = "(SELECT id from events.domino_boletus where round_id = '" + round_id + "') "
    
    #Posicionamiento
    str_loterry = "DELETE FROM events.trace_lottery_manual WHERE tourney_id = '" + tourney_id + "'; " 
    str_scale = "DELETE FROM events.domino_rounds_scale " + str_round +\
        "DELETE FROM events.domino_rounds_pairs " + str_round
    
    #boleta
    domino_boletus = "DELETE from events.domino_boletus_position where boletus_id IN " + str_id_boletus + "; " +\
        "DELETE from events.domino_boletus_data where boletus_id IN " + str_id_boletus + "; " +\
        "DELETE from events.domino_boletus_pairs where boletus_id IN " + str_id_boletus + "; "
        
    domino_boletus += "DELETE FROM events.domino_boletus where round_id = '" + round_id + "'; " 
    domino_boletus += "DELETE FROM events.domino_boletus where round_id = '" + round_id + "'; " 
    
    # cambiar el estado de los jugadores estado confirmados
    status_play = get_one_status_by_name('CONFIRMED', db=db)
    status_canceled = get_one_status_by_name('CANCELLED', db=db)
    status_expeled = get_one_status_by_name('EXPELLED', db=db)
    status_init = get_one_status_by_name('CREATED', db=db)
    
    str_update_player = "UPDATE events.players SET status_id=" + str(status_play.id) +\
        " WHERE tourney_id = '" + tourney_id + "' and status_id not in (" + str(status_canceled.id) + "," + str(status_expeled.id) + ") ; "
        
    str_update_round = "UPDATE events.domino_rounds SET status_id=" + str(status_init.id) +\
        " WHERE id = '" + round_id + "'; "
        
    str_delete = str_loterry + domino_boletus + str_scale + str_update_player + str_update_round + "COMMIT; " 
    db.execute(str_delete)
    db.commit()
    
    return True     
