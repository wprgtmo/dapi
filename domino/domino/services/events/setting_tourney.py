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
from domino.schemas.events.domino_rounds import DominoRoundsAperture

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
from domino.services.resources.playercategories import get_one_event_scope_by_name, get_one_event_level_by_name

from domino.services.events.domino_table import created_tables_default
from domino.services.events.domino_round import created_round_default, remove_configurate_round, get_last_by_tourney, get_one_by_number
from domino.services.events.domino_scale import aperture_one_new_round
from domino.services.events.invitations import get_amount_invitations_by_tourney

from domino.services.events.tourney import get_one as get_one_tourney, calculate_amount_tables, \
    get_count_players_by_tourney, get_values_elo_by_tourney, get_lst_categories_of_tourney, get_categories_of_tourney,\
    create_category_by_default, update_amount_player_by_categories, calculate_amount_categories, \
    calculate_amount_players_playing, created_segmentation_by_level
from domino.services.enterprise.auth import get_url_advertising

def get_one_configure_tourney(request:Request, tourney_id: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()  
    
    db_tourney = get_one_tourney(tourney_id=tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))

    amount_tables = calculate_amount_tables(tourney_id=tourney_id, modality=db_tourney.modality, db=db) 
    
    if db_tourney.amount_tables != amount_tables:
        db_tourney.amount_tables = amount_tables
        db.add(db_tourney)
        db.commit()
    
    #actualizar la cantidad de jugadores por categorias
    update_amount_player_by_categories(tourney_id, db=db)
    
    elo_max, elo_min = get_values_elo_by_tourney(tourney_id=tourney_id, db=db)
    
    result.data = {
        "tourney_id": tourney_id, "amount_tables": amount_tables, 'number_rounds': db_tourney.number_rounds,
        "name": '' if not db_tourney.name else db_tourney.name,
        "modality": '' if not db_tourney.modality else db_tourney.modality,
        "summary": '' if not db_tourney.summary else db_tourney.summary,
        "start_date": '' if not db_tourney.start_date else db_tourney.start_date,
        'amount_player': get_count_players_by_tourney(tourney_id, db=db),
        "amount_smart_tables": 0 if not db_tourney.amount_smart_tables else db_tourney.amount_smart_tables,
        "use_segmentation": True if db_tourney.use_segmentation else False,
        'amount_segmentation_round': 0 if not db_tourney.amount_segmentation_round else db_tourney.amount_segmentation_round,
        "segmentation_type": db_tourney.segmentation_type if db_tourney.segmentation_type else 'ELO',
        # "use_penalty": True if db_tourney.use_penalty else False,
        # "use_bonus": True if db_tourney.use_bonus else False,
        "absences_point": db_tourney.points_for_absences if  db_tourney.points_for_absences else 0 if not db_tourney.number_points_to_win else db_tourney.number_points_to_win,
        # "amount_bonus_tables": 0 if not db_tourney.amount_bonus_tables else db_tourney.amount_bonus_tables,
        # "amount_bonus_points": 0 if not db_tourney.amount_bonus_points else db_tourney.amount_bonus_points,
        # "amount_bonus_points_rounds": 0 if not db_tourney.amount_bonus_points_rounds else db_tourney.amount_bonus_points_rounds,
        "number_points_to_win": 0 if not db_tourney.number_points_to_win else db_tourney.number_points_to_win,
        "time_to_win": 0 if not db_tourney.time_to_win else db_tourney.time_to_win,
        "game_system": 'SUIZO' if not db_tourney.game_system else db_tourney.game_system,
        'lottery_type': 'MANUAL' if not db_tourney.lottery_type else db_tourney.lottery_type,
        # 'penalties_limit': 0 if not db_tourney.penalties_limit else db_tourney.penalties_limit,
        # 'points_penalty_yellow': 0 if not db_tourney.points_penalty_yellow else db_tourney.points_penalty_yellow,
        # 'points_penalty_red': 0 if not db_tourney.points_penalty_red else db_tourney.points_penalty_red,
        'elo_min': elo_min, 'elo_max': elo_max,
        'constant_increase_ELO': 16 if not db_tourney.constant_increase_elo else db_tourney.constant_increase_elo,
        'round_ordering_one': '' if not db_tourney.round_ordering_one else db_tourney.round_ordering_one,
        'round_ordering_dir_one': 'ASC' if not db_tourney.round_ordering_dir_one else db_tourney.round_ordering_dir_one,
        'round_ordering_two': '' if not db_tourney.round_ordering_two else db_tourney.round_ordering_two,
        'round_ordering_dir_two': 'ASC' if not db_tourney.round_ordering_dir_two else db_tourney.round_ordering_dir_two,
        'round_ordering_three': '' if not db_tourney.round_ordering_three else db_tourney.round_ordering_three,
        'round_ordering_dir_three': 'ASC' if not db_tourney.round_ordering_dir_three else db_tourney.round_ordering_dir_three,
        'event_ordering_one': '' if not db_tourney.event_ordering_one else db_tourney.event_ordering_one,
        'event_ordering_dir_one': 'ASC' if not db_tourney.event_ordering_dir_one else db_tourney.event_ordering_dir_one,
        'event_ordering_two': '' if not db_tourney.event_ordering_two else db_tourney.event_ordering_two,
        'event_ordering_dir_two': 'ASC' if not db_tourney.event_ordering_dir_two else db_tourney.event_ordering_dir_two,
        'event_ordering_three': '' if not db_tourney.event_ordering_three else db_tourney.event_ordering_three,
        'event_ordering_dir_three': 'ASC' if not db_tourney.event_ordering_dir_three else db_tourney.event_ordering_dir_three,
        'status_id': db_tourney.status_id,
        'lst_categories': get_lst_categories_of_tourney(tourney_id=tourney_id, db=db),
        'status_name': db_tourney.status.name,
        'status_description': db_tourney.status.description,
        'scope': db_tourney.scope.id if db_tourney.scope else '',
        'level': db_tourney.level.id if db_tourney.level else ''
        }
        
    return result

def configure_one_tourney(request, tourney_id: str, settingtourney: SettingTourneyCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_tourney = get_one_tourney(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    validate_atributes_requiered(
        db_tourney, locale, settingtourney.number_points_to_win, settingtourney.time_to_win, name, settingtourney.number_rounds)
    
    amount_tables = calculate_amount_tables(db_tourney.id, db_tourney.modality, db=db)
    restart_setting_round = False
    if amount_tables < 2:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.number_player_incorrect"))

    # para cambiar la modalidad debo verificar si ya se enviaron invitaciones o no. 
    if settingtourney.modality and db_tourney.modality != str(settingtourney.modality):
        amount_invitations = get_amount_invitations_by_tourney(tourney_id, db=db)
        if amount_invitations > 0:
            raise HTTPException(status_code=404, detail=_(locale, "tourney.sended_invitations"))
        
        if db_tourney.status.name != 'CREATED':
            raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
        db_tourney.modality = str(settingtourney.modality)
        
    if settingtourney.amount_smart_tables and db_tourney.amount_smart_tables != settingtourney.amount_smart_tables:
        restart_setting_round = True
        if int(settingtourney.amount_smart_tables) > amount_tables:
            raise HTTPException(status_code=404, detail=_(locale, "tourney.smarttable_incorrect"))
        else:
            db_tourney.amount_smart_tables = settingtourney.amount_smart_tables
    
    if settingtourney.number_points_to_win and db_tourney.number_points_to_win != int(settingtourney.number_points_to_win):
        if db_tourney.status.name not in ('CREATED', 'CONFIGURATED'):
            raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
        db_tourney.number_points_to_win = int(settingtourney.number_points_to_win)
        
    if settingtourney.absences_point and db_tourney.points_for_absences != int(settingtourney.absences_point):
        if db_tourney.status.name not in ('CREATED', 'CONFIGURATED'):
            raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
        db_tourney.points_for_absences = int(settingtourney.absences_point)
    
    if not db_tourney.points_for_absences:
        db_tourney.points_for_absences = db_tourney.number_points_to_win
    
    if settingtourney.time_to_win and db_tourney.time_to_win != int(settingtourney.time_to_win):
        if db_tourney.status.name not in ('CREATED', 'CONFIGURATED'):
            raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
        db_tourney.time_to_win = int(settingtourney.time_to_win)
    
    # por ahora no se va a pedir
    db_tourney.game_system = 'SUIZO'
    
    if settingtourney.lottery and db_tourney.lottery_type != str(settingtourney.lottery):
        restart_setting_round = True
        db_tourney.lottery_type = str(settingtourney.lottery)
    db_tourney.lottery_type = 'MANUAL' if not db_tourney.lottery_type else db_tourney.lottery_type
    
    if settingtourney.constant_increase_ELO and db_tourney.constant_increase_elo != float(settingtourney.constant_increase_ELO):
        db_tourney.constant_increase_elo = int(settingtourney.constant_increase_ELO)
        
    # use_penalty = True if settingtourney.use_penalty and settingtourney.use_penalty == True else False
    # if db_tourney.use_penalty != use_penalty:
    #     if not settingtourney.limitPenaltyPoints:
    #         raise HTTPException(status_code=404, detail=_(locale, "tourney.limitpenalty_incorrect"))
    #     if not settingtourney.points_penalty_yellow:
    #         raise HTTPException(status_code=404, detail=_(locale, "tourney.penaltyyelloew_incorrect"))
    #     if not settingtourney.points_penalty_red:
    #         raise HTTPException(status_code=404, detail=_(locale, "tourney.penaltyred_incorrect"))
        
    #     db_tourney.use_penalty = use_penalty
    #     if db_tourney.penalties_limit != int(settingtourney.limitPenaltyPoints):
    #         db_tourney.penalties_limit = int(settingtourney.limitPenaltyPoints)
        
    #     if db_tourney.points_penalty_yellow != int(settingtourney.points_penalty_yellow):
    #         db_tourney.points_penalty_yellow = int(settingtourney.points_penalty_yellow)
            
    #     if db_tourney.points_penalty_red != int(settingtourney.points_penalty_red):
    #         db_tourney.points_penalty_red = int(settingtourney.points_penalty_red)
        
    use_segmentation = True if settingtourney.use_segmentation and settingtourney.use_segmentation == True else False
    if db_tourney.use_segmentation != use_segmentation:
        restart_setting_round = True
        db_tourney.use_segmentation = use_segmentation
    
    if db_tourney.use_segmentation:  
        # validar que todos los jugadores del torneo estén incluidos en los rangos de categorias.
        # validar si todos los jugadores del torneo están en alguna categoria
        
        settingtourney.segmentation_type = 'NIVEL'
        if not settingtourney.segmentation_type:
            raise HTTPException(status_code=404, detail=_(locale, "tourney.segmentation_type_is_req"))
        
        if not settingtourney.amount_segmentation_round:
            raise HTTPException(status_code=404, detail=_(locale, "tourney.amount_segmentation_round_is_req"))
        
        if settingtourney.segmentation_type == 'NIVEL':
            # crear las categorias de nivel if no existen
            created_segmentation_by_level(tourney_id=tourney_id, db=db)
            
        if not verify_players_by_category(db_tourney.id, db=db):
            raise HTTPException(status_code=404, detail=_(locale, "tourney.exist_player_not_categories"))
        
        if db_tourney.segmentation_type != settingtourney.segmentation_type:
            db_tourney.segmentation_type = settingtourney.segmentation_type
            
        if db_tourney.amount_segmentation_round != settingtourney.amount_segmentation_round:
            db_tourney.amount_segmentation_round = settingtourney.amount_segmentation_round
            
    last_round, prevoius_round = None, None  
    if use_segmentation:
        # debo verificar si existe una ronda anterior y en esta no se uso categoria, no se puede modificar el dato ya.
        last_round = get_last_by_tourney(db_tourney.id, db=db)
        if last_round:
            if last_round.round_number != 1 : #estamos en la primera, no tengo que buscar
                prevoius_round = get_one_by_number(last_round.round_number, db=db)
                if prevoius_round and prevoius_round.use_segmentation is False:
                    raise HTTPException(status_code=404, detail=_(locale, "tourney.round_not_cant_categories"))
        
        amount_category = calculate_amount_categories(db_tourney.id, db=db)
        if amount_category < 1:
            raise HTTPException(status_code=404, detail=_(locale, "tourney.amount_categories_incorrect"))
        
    # use_bonus = True if settingtourney.use_bonus and settingtourney.use_bonus == True else False
    # if use_bonus:
    #     # debo verificar si existe una ronda anterior y en esta no se uso bonificacion, no se puede modificar el dato ya.
    #     if not last_round:
    #         last_round = get_last_by_tourney(db_tourney.id, db=db)
    #         if last_round:
    #             prevoius_round = get_one_by_number(last_round.number_round, db=db)
    #             if prevoius_round and prevoius_round.use_bonus is True:
    #                 raise HTTPException(status_code=404, detail=_(locale, "tourney.round_not_cant_bonus"))
        
    #     if not settingtourney.amount_bonus_tables:
    #         raise HTTPException(status_code=404, detail=_(locale, "tourney.amount_bonus_tables_incorrect"))
    #     if int(settingtourney.amount_bonus_tables) <= 0:
    #         raise HTTPException(status_code=404, detail=_(locale, "tourney.amount_bonus_tables_incorrect"))
    #     if not settingtourney.amount_bonus_points:
    #         raise HTTPException(status_code=404, detail=_(locale, "tourney.amount_bonus_tables_incorrect"))
    #     if int(settingtourney.amount_bonus_points) <= 0:
    #         raise HTTPException(status_code=404, detail=_(locale, "tourney.amount_bonus_tables_incorrect"))
    #     if int(settingtourney.amount_bonus_points_rounds) <= 0:
    #         raise HTTPException(status_code=404, detail=_(locale, "tourney.amount_bonus_tables_incorrect"))
        
    #     if db_tourney.use_bonus != use_bonus:
    #         db_tourney.use_bonus = use_bonus
        
    #     if db_tourney.amount_bonus_tables != int(settingtourney.amount_bonus_tables):
    #         db_tourney.amount_bonus_tables = int(settingtourney.amount_bonus_tables)
            
    #     if db_tourney.amount_bonus_points != int(settingtourney.amount_bonus_points):
    #         db_tourney.amount_bonus_points = int(settingtourney.amount_bonus_points)
            
    #     if db_tourney.amount_bonus_points_rounds != int(settingtourney.amount_bonus_points_rounds):
    #         db_tourney.amount_bonus_points_rounds = int(settingtourney.amount_bonus_points_rounds)
            
    if settingtourney.round_ordering_one and db_tourney.round_ordering_one != str(settingtourney.round_ordering_one):
        db_tourney.round_ordering_one = str(settingtourney.round_ordering_one)
    if settingtourney.round_ordering_dir_one and db_tourney.round_ordering_dir_one != str(settingtourney.round_ordering_dir_one):
        db_tourney.round_ordering_dir_one = str(settingtourney.round_ordering_dir_one)
    if not db_tourney.round_ordering_dir_one:
        db_tourney.round_ordering_dir_one = "DESC" 
        
    if settingtourney.round_ordering_two and db_tourney.round_ordering_two != str(settingtourney.round_ordering_two):
        db_tourney.round_ordering_two = str(settingtourney.round_ordering_two)
    if settingtourney.round_ordering_dir_two and db_tourney.round_ordering_dir_two != str(settingtourney.round_ordering_dir_two):
        db_tourney.round_ordering_dir_two = str(settingtourney.round_ordering_dir_two)
    if not db_tourney.round_ordering_dir_two:
        db_tourney.round_ordering_dir_two = "DESC" 
        
    if settingtourney.round_ordering_three and db_tourney.round_ordering_three != str(settingtourney.round_ordering_three):
        db_tourney.round_ordering_three = str(settingtourney.round_ordering_three)
    if settingtourney.round_ordering_dir_three and db_tourney.round_ordering_dir_three != str(settingtourney.round_ordering_dir_three):
        db_tourney.round_ordering_dir_three = str(settingtourney.round_ordering_dir_three)
    if not db_tourney.round_ordering_dir_three:
        db_tourney.round_ordering_dir_three = "DESC" 
            
    if not db_tourney.round_ordering_one or not db_tourney.round_ordering_two or not db_tourney.round_ordering_three:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.round_ordering_incorrect"))
            
    if settingtourney.event_ordering_one and db_tourney.event_ordering_one != str(settingtourney.event_ordering_one):
        db_tourney.event_ordering_one = str(settingtourney.event_ordering_one)
    if settingtourney.event_ordering_dir_one and db_tourney.event_ordering_dir_one != str(settingtourney.event_ordering_dir_one):
        db_tourney.event_ordering_dir_one = str(settingtourney.event_ordering_dir_one)
    if not db_tourney.event_ordering_dir_one:
        db_tourney.event_ordering_dir_one = "DESC" 
    
    if settingtourney.event_ordering_two and db_tourney.event_ordering_two != str(settingtourney.event_ordering_two):
        db_tourney.event_ordering_two = str(settingtourney.event_ordering_two)
    if settingtourney.event_ordering_dir_two and db_tourney.event_ordering_dir_two != str(settingtourney.event_ordering_dir_two):
        db_tourney.event_ordering_dir_two = str(settingtourney.event_ordering_dir_two)
    if not db_tourney.event_ordering_dir_two:
        db_tourney.event_ordering_dir_two = "DESC" 
        
    if settingtourney.event_ordering_three and db_tourney.event_ordering_three != str(settingtourney.event_ordering_three):
        db_tourney.event_ordering_three = str(settingtourney.event_ordering_three)
    if settingtourney.event_ordering_dir_three and db_tourney.event_ordering_dir_three != str(settingtourney.event_ordering_dir_three):
        db_tourney.event_ordering_dir_three = str(settingtourney.event_ordering_dir_three)
    if not db_tourney.event_ordering_dir_three:
        db_tourney.event_ordering_dir_three = "DESC" 
        
    if not db_tourney.event_ordering_one or not db_tourney.event_ordering_two or not db_tourney.event_ordering_three:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.event_ordering_incorrect"))
    
    if db_tourney.name != str(settingtourney.name):
        db_tourney.name = str(settingtourney.name)
        
    if settingtourney.summary and db_tourney.summary != str(settingtourney.summary):
        db_tourney.summary = str(settingtourney.summary)
        
    if settingtourney.start_date and db_tourney.start_date != settingtourney.start_date:
        db_tourney.start_date = settingtourney.start_date
        
    if settingtourney.number_rounds and db_tourney.number_rounds != int(settingtourney.number_rounds):
        db_tourney.number_rounds = int(settingtourney.number_rounds)
    
    if settingtourney.scope_tourney:
        db_scope = get_one_event_scope_by_name(settingtourney.scope_tourney, db=db)
        if db_scope and db_tourney.scope_tourney != db_scope.id:
            db_tourney.scope_tourney = db_scope.id
    if not db_tourney.scope_tourney:
        db_scope = get_one_event_scope_by_name('Local', db=db)
        db_tourney.scope_tourney = db_scope.id
        
    if settingtourney.level_tourney:
        db_level = get_one_event_level_by_name(settingtourney.level_tourney, db=db)
        if db_level and db_tourney.level_tourney != db_level.id:
            db_tourney.level_tourney = db_level.id
    if not db_tourney.level_tourney:
        db_level = get_one_event_level_by_name('1', db=db)
        db_tourney.level_tourney = db_level.id
        
    db_tourney.updated_by=currentUser['username']
    
    restart_setting_round = True if not restart_setting_round and db_tourney.lottery_type == 'AUTOMATIC' else restart_setting_round
     
    if restart_setting_round:
        update_initializes_tourney(db_tourney, locale, db=db)
    
    db.add(db_tourney)
    db.commit()
    
    return result

def validate_atributes_requiered(db_tourney, locale, number_points_to_win, time_to_win,  name, number_rounds):
    
    if db_tourney.status.name == 'FINALIZED':
        raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
    if number_points_to_win <= 0:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.numberpoints_towin_incorrect"))
    
    if time_to_win <= 0:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.time_to_win_incorrect"))
    
    if not name:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.name_incorrect"))
    
    if not number_rounds:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.number_rounds_incorrect"))
    
    return True

def verify_players_by_category(tourney_id, db:Session):
    
    str_count = "SELECT count(id) FROM events.players_users  pu join events.players pa ON pa.id = pu.player_id " +\
        "Where pa.tourney_id = '" + str(tourney_id) + "' AND category_id is NULL "
        
    count_round = db.execute(str_count).fetchone()[0]
    
    return True if count_round == 0 else False
  
def update_initializes_tourney(db_tourney, locale, db:Session):
    
    # esto es por si se queda por calculos
    # divmod_round = divmod(db_tourney.amount_rounds,5)
    
    # db_tourney.amount_smart_tables = amount_smart_tables
    # db_tourney.amount_rounds = db_tourney.amount_rounds
    # db_tourney.use_bonus = False
    # db_tourney.amount_bonus_tables = db_tourney.amount_rounds // 4 
    # db_tourney.amount_bonus_points = (db_tourney.amount_rounds // 4) * 2
    # db_tourney.number_bonus_round = db_tourney.amount_rounds + 1 if db_tourney.amount_rounds <= 9 else 4 if db_tourney.amount_rounds <= 15 else \
    #     divmod_round[0] if divmod_round[1] == 0 else divmod_round[0] + 1
    
    elo_max, elo_min = get_values_elo_by_tourney(tourney_id=db_tourney.id, db=db)
    
    db_tourney.elo_max = elo_max
    db_tourney.elo_min = elo_min
       
    # crear las mesas y si ya están creadas borrar y volver a crear
    
    db_round_ini = get_last_by_tourney(db_tourney.id, db=db)
    if db_round_ini:
        result_init = remove_configurate_round(db_tourney.id, db_round_ini.id, db=db)
        status_creat = get_one_status_by_name('CREATED', db=db)
        db_round_ini.status_id = status_creat.id
        
    result_init = created_tables_default(db_tourney, db)
    if not result_init:
        raise HTTPException(status_code=400, detail=_(locale, "tourney.setting_tables_failed"))
    
    # crear la primera ronda, si ya existe, no hacer nada.
    if not db_round_ini:
        db_round_ini = created_round_default(db_tourney, 'Ronda Nro. 1', db=db, round_number=1, is_first=True)
        if not db_round_ini:
            raise HTTPException(status_code=400, detail=_(locale, "tourney.setting_rounds_failed"))
    
    if db_tourney.segmentation_type == 'ELO':
        # actualizar elos de las categorias si existen
        lst_category = get_categories_of_tourney(tourney_id=db_tourney.id, db=db)
        if lst_category:
            first_category, last_category = None, None
            for item in lst_category:
                if not first_category:
                    first_category = item 
                last_category = item
            if first_category and first_category.elo_max != elo_max:
                first_category.elo_max = elo_max 
                db.add(first_category)
                
            if last_category and last_category.elo_min != elo_min:
                last_category.elo_min = elo_min 
                db.add(last_category)
        else:
            create_category_by_default(db_tourney.id, elo_max, elo_min, amount_players=0, db=db)
        
    # si el sorteo es automático, ya debo crear la primera distribución.
    if db_tourney.lottery_type == "AUTOMATIC":
        # round_created = DominoRoundsAperture(use_segmentation=db_tourney.use_segmentation, use_bonus=False, #db_tourney.use_bonus,
        #                                      amount_bonus_tables=db_tourney.amount_bonus_tables, amount_bonus_points=db_tourney.amount_bonus_points)
        round_created = DominoRoundsAperture(use_segmentation=db_tourney.use_segmentation, use_bonus=False, 
                                             amount_bonus_tables=0, amount_bonus_points=0)
        aperture_one_new_round(db_round_ini.id, round_created, locale, db=db)
    
    # try:
    
    return True
       
    # except (Exception, SQLAlchemyError, IntegrityError) as e:
    #     return False