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

from domino.schemas.resources.result_object import ResultObject
from domino.schemas.events.tourney import SettingTourneyCreated

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
from domino.services.enterprise.users import get_one_by_username
from domino.services.enterprise.userprofile import get_one as get_one_profile
from domino.services.events.domino_boletus import created_boletus_for_round

from domino.services.events.domino_table import created_tables_default
from domino.services.events.domino_round import created_round_default
from domino.services.events.domino_scale import configure_automatic_lottery, update_elo_initial_scale

from domino.services.events.tourney import get_one as get_one_tourney, calculate_amount_tables, \
    get_count_players_by_tourney, get_values_elo_by_tourney
from domino.services.enterprise.auth import get_url_advertising

def get_one_configure_tourney(request:Request, tourney_id: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()  
    
    api_uri = str(settings.api_uri)
    
    db_tourney = get_one_tourney(tourney_id=tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))

    amount_tables = calculate_amount_tables(tourney_id=tourney_id, modality=db_tourney.modality, db=db) 
    
    if db_tourney.amount_tables != amount_tables:
        db_tourney.amount_tables = amount_tables
        db.add(db_tourney)
        db.commit()
    
    elo_max, elo_min = get_values_elo_by_tourney(tourney_id=tourney_id, db=db)
    
    result.data = {
        "tourney_id": tourney_id, "amount_tables": amount_tables,
        'amount_player': get_count_players_by_tourney(tourney_id, db=db),
        "amount_smart_tables": 0 if not db_tourney.amount_smart_tables else db_tourney.amount_smart_tables,
        "amount_rounds": 0 if not db_tourney.number_rounds else db_tourney.number_rounds,
        "use_bonus": 'NO', #if not db_tourney.amount_smart_tables else 'YES' if setting.use_bonus else 'NO',
        "amount_bonus_tables": 0 if not db_tourney.number_bonus_round else db_tourney.number_bonus_round,
        "amount_bonus_points": 0 if not db_tourney.amount_bonus_points else db_tourney.amount_bonus_points,
        "number_bonus_round": 0 if not db_tourney.number_bonus_round else db_tourney.number_bonus_round,
        "number_points_to_win": 0 if not db_tourney.number_points_to_win else db_tourney.number_points_to_win,
        "time_to_win": 0 if not db_tourney.time_to_win else db_tourney.time_to_win,
        "game_system": 'SUIZO' if not db_tourney.game_system else db_tourney.game_system,
        'lottery_type': 'MANUAL' if not db_tourney.lottery_type else db_tourney.lottery_type,
        'penalties_limit': 0 if not db_tourney.penalties_limit else db_tourney.penalties_limit,
        'elo_min': elo_min, 'elo_max': elo_max,
        'image': get_url_advertising(tourney_id=tourney_id, file_name=db_tourney.image, api_uri=api_uri),
        'status_id': db_tourney.status_id,
        'lst_categories': get_lst_categories_of_tourney(tourney_id=tourney_id, db=db),
        'status_name': db_tourney.status.name,
        'status_description': db_tourney.status.description
        }
    
    return result
    
def get_lst_categories_of_tourney(tourney_id: str, db: Session):
    
    lst_categories = []
    
    str_query = "SELECT id, category_number, position_number, elo_min, elo_max, amount_players " +\
        "FROM events.domino_categories WHERE tourney_id = '" + tourney_id + "' Order by position_number "
        
    lst_all_category = db.execute(str_query).fetchall()
    for item in lst_all_category:
        lst_categories.append({'category_number': item.category_number,
                              'position_number': item.position_number,
                              'amount_players': item.amount_players,
                              'elo_min': item.elo_min, 'elo_max': item.elo_max})
    return lst_categories

# def close_configure_one_tourney(request, tourney_id: str, db: Session):
#     locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
#     result = ResultObject() 
#     currentUser = get_current_user(request)
    
#     one_status_conf = get_one_status_by_name('CONFIGURATED', db=db)
    
#     str_query = "SELECT count(tourney_id) FROM events.domino_categories where tourney_id = '" + tourney_id + "' "
#     amount = db.execute(str_query).fetchone()[0]
#     if amount == 0:
#         raise HTTPException(status_code=404, detail=_(locale, "tourney.category_not_configurated"))
    
#     db_tourney = get_one_tourney(tourney_id, db=db)
#     if not db_tourney:
#         raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
#     try:
#         elo_max, elo_min = get_values_elo_by_tourney(tourney_id=tourney_id, modality=db_tourney.modality, db=db)
        
#         lst_category = get_lst_categories_of_tourney(tourney_id=tourney_id, db=db)
        
#         db_tourney.elo_max = elo_max
#         db_tourney.elo_min = elo_min
#         db.add(db_tourney)
#         db.commit()
#     except:
#         raise HTTPException(status_code=404, detail=_(locale, "tourney.error_at_closed"))
    
#     # validar todas las categorias estén contempladas entre los elo de los jugadores.
#     if not verify_category_is_valid(float(elo_max), float(elo_min), lst_category=lst_category):
#         raise HTTPException(status_code=400, detail=_(locale, "tourney.setting_category_incorrect"))
    
#     # crear las mesas y sus ficheros
#     result_init = configure_domino_tables(
#         db_tourney, db, currentUser['username'], file=None)
#     if not result_init:
#         raise HTTPException(status_code=400, detail=_(locale, "tourney.setting_tables_failed"))
    
#     # crear la primera ronda
#     db_round_ini = configure_new_rounds(db_tourney.id, 'Ronda Nro. 1', db=db, created_by=currentUser['username'],
#                                         round_number=1)
#     if not db_round_ini:
#         raise HTTPException(status_code=400, detail=_(locale, "tourney.setting_rounds_failed"))
    
#     db_tourney.updated_by = currentUser['username']
    
#     if db_tourney.lottery_type  == 'AUTOMATIC':
#         one_status_init = get_one_status_by_name('INITIADED', db=db)
        
#         # si el sorteo es automático, crear el sorteo inicial, y ya iniciar evento y torneo
#         result_init = configure_automatic_lottery(db_tourney, db_round_ini, one_status_init, db=db)
#         if not result_init:
#             raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_initial_scale_failed"))
        
#     else:
#         db_tourney.status_id = one_status_conf.id
    
#     try:
#         db.add(db_tourney)
#         db.commit()
#     except:
#         raise HTTPException(status_code=404, detail=_(locale, "tourney.error_at_closed"))
    
#     return result

def verify_category_is_valid(elo_max: float, elo_min: float, lst_category: list):
    
    current_elo_max = float(elo_max)
    current_elo_min = float(elo_min)
    for item in lst_category:
        if current_elo_max !=  float(item['elo_max']):
            return False
        else:
            current_elo_max = float(item['elo_min']) - 1 
            current_elo_min = float(item['elo_min'])
    
    if current_elo_min != float(elo_min):
        return False
    
    return True

def configure_one_tourney(request, tourney_id: str, settingtourney: SettingTourneyCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    # este metod se va a llmara cualquier cantidad de veces, debo revisar y sobreescribir todo.
    one_status_end = get_one_status_by_name('FINALIZED', db=db)
    
    db_tourney = get_one_tourney(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    if db_tourney.status_id == one_status_end.id:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
    amount_tables = calculate_amount_tables(db_tourney.id, db_tourney.modality, db=db)
    
    try:
        amount_smart_tables = int(settingtourney['amount_smart_tables'])
        amount_rounds = int(settingtourney['amount_rounds'])
        number_points_to_win = int(settingtourney['number_points_to_win'])
        time_to_win = int(settingtourney['time_to_win'])
        time_to_win = 12 if not time_to_win else time_to_win
        game_system = str(settingtourney['game_system'])
        game_system = 'SUIZO' if not game_system else game_system
        lottery_type = str(settingtourney['lottery'])
        lottery_type = 'MANUAL' if not lottery_type else lottery_type
        penalties_limit = int(settingtourney['limitPenaltyPoints'])
        use_bonus = True if str(settingtourney['bonus']) == 'YES' else False 
        
    except:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_incorrect"))
    
    if amount_smart_tables > amount_tables:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.smarttable_incorrect"))
    
    if amount_rounds <= 0:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.amountrounds_incorrect"))
    
    if number_points_to_win <= 0:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.numberpoints_towin_incorrect"))
    
    db_tourney.updated_by=currentUser['username']
    
    update_initializes_tourney(db_tourney, amount_smart_tables, amount_rounds, number_points_to_win, 
                                time_to_win, game_system, use_bonus, lottery_type, penalties_limit, db=db,
                                locale=lottery_type)
    
    return result

def update_initializes_tourney(db_tourney, amount_smart_tables, amount_rounds, number_points_to_win, 
                        time_to_win, game_system, use_bonus, lottery_type, penalties_limit, db: Session,
                        locale):
    
    divmod_round = divmod(amount_rounds,5)
    
    db_tourney.amount_smart_tables = amount_smart_tables
    db_tourney.amount_rounds = amount_rounds
    db_tourney.use_bonus = use_bonus
    db_tourney.amount_bonus_tables = amount_rounds // 4 
    db_tourney.amount_bonus_points = (amount_rounds // 4) * 2
    db_tourney.number_bonus_round = amount_rounds + 1 if amount_rounds <= 9 else 4 if amount_rounds <= 15 else \
        divmod_round[0] if divmod_round[1] == 0 else divmod_round[0] + 1
    db_tourney.number_points_to_win = number_points_to_win
    
    db_tourney.time_to_win = time_to_win
    db_tourney.game_system = game_system
    db_tourney.lottery_type = lottery_type
    db_tourney.penalties_limit = penalties_limit
    
    elo_max, elo_min = get_values_elo_by_tourney(tourney_id=db_tourney.id, db=db)
    
    db_tourney.elo_max = elo_max
    db_tourney.elo_min = elo_min
       
    # crear las mesas y si ya están creadas borrar y volver a crear
    result_init = created_tables_default(db_tourney, db)
    if not result_init:
        raise HTTPException(status_code=400, detail=_(locale, "tourney.setting_tables_failed"))
    
    # crear la primera ronda, si ya existe, no hacer nada.
    db_round_ini = created_round_default(db_tourney, 'Ronda Nro. 1', db=db, round_number=1, is_first=True)
    if not db_round_ini:
        raise HTTPException(status_code=400, detail=_(locale, "tourney.setting_rounds_failed"))
    
    try:
        db.add(db_tourney)
        db.commit()
        return True
       
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return False