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
from domino.services.events.domino_round import created_round_default, remove_configurate_round, get_last_by_tourney
from domino.services.events.domino_scale import configure_automatic_lottery, update_elo_initial_scale
from domino.services.events.invitations import get_amount_invitations_by_tourney

from domino.services.events.tourney import get_one as get_one_tourney, calculate_amount_tables, \
    get_count_players_by_tourney, get_values_elo_by_tourney, get_lst_categories_of_tourney, get_categories_of_tourney,\
    create_category_by_default, update_amount_player_by_categories
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
        "use_segmentation": 'NO' if not db_tourney.use_segmentation else 'YES',
        "use_penalty": 'NO' if not db_tourney.use_penalty else 'YES',
        "use_bonus": 'NO' if not db_tourney.use_bonus else 'YES',
        "amount_bonus_tables": 0 if not db_tourney.amount_bonus_tables else db_tourney.amount_bonus_tables,
        "amount_bonus_points": 0 if not db_tourney.amount_bonus_points else db_tourney.amount_bonus_points,
        "number_points_to_win": 0 if not db_tourney.number_points_to_win else db_tourney.number_points_to_win,
        "time_to_win": 0 if not db_tourney.time_to_win else db_tourney.time_to_win,
        "game_system": 'SUIZO' if not db_tourney.game_system else db_tourney.game_system,
        'lottery_type': 'MANUAL' if not db_tourney.lottery_type else db_tourney.lottery_type,
        'penalties_limit': 0 if not db_tourney.penalties_limit else db_tourney.penalties_limit,
        'points_penalty_yellow': 0 if not db_tourney.points_penalty_yellow else db_tourney.points_penalty_yellow,
        'points_penalty_red': 0 if not db_tourney.points_penalty_red else db_tourney.points_penalty_red,
        'elo_min': elo_min, 'elo_max': elo_max,
        'constant_increase_ELO': 0 if not db_tourney.constant_increase_elo else db_tourney.constant_increase_elo,
        'round_ordering_one': '' if not db_tourney.round_ordering_one else db_tourney.round_ordering_one,
        'round_ordering_two': '' if not db_tourney.round_ordering_two else db_tourney.round_ordering_two,
        'round_ordering_three': '' if not db_tourney.round_ordering_three else db_tourney.round_ordering_three,
        'event_ordering_one': '' if not db_tourney.event_ordering_one else db_tourney.event_ordering_one,
        'event_ordering_two': '' if not db_tourney.event_ordering_two else db_tourney.event_ordering_two,
        'event_ordering_three': '' if not db_tourney.event_ordering_three else db_tourney.event_ordering_three,
        'status_id': db_tourney.status_id,
        'lst_categories': get_lst_categories_of_tourney(tourney_id=tourney_id, db=db),
        'status_name': db_tourney.status.name,
        'status_description': db_tourney.status.description
        }
        
    return result

def configure_one_tourney(request, tourney_id: str, settingtourney: SettingTourneyCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_tourney = get_one_tourney(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    if db_tourney.status.name == 'FINALIZED':
        raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
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
        if db_tourney.status.name != 'CREATED':
            raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
        if int(settingtourney.number_points_to_win) <= 0:
            raise HTTPException(status_code=404, detail=_(locale, "tourney.numberpoints_towin_incorrect"))
        db_tourney.number_points_to_win = int(settingtourney.number_points_to_win)
        
    if settingtourney.time_to_win and db_tourney.time_to_win != int(settingtourney.time_to_win):
        db_tourney.time_to_win = int(settingtourney.time_to_win)
    
    db_tourney.time_to_win = 12 if not db_tourney.time_to_win else db_tourney.time_to_win
    
    # por ahora no se va a pedir
    db_tourney.game_system = 'SUIZO'
    
    if settingtourney.lottery and db_tourney.lottery_type != str(settingtourney.lottery):
        db_tourney.lottery_type = str(settingtourney.lottery)
    db_tourney.lottery_type = 'MANUAL' if not db_tourney.lottery_type else db_tourney.lottery_type
    
    use_penalty = True if settingtourney.use_penalty and settingtourney.use_penalty == 'YES' else False
    if db_tourney.use_penalty != use_penalty:
        db_tourney.use_penalty = use_penalty
        
    use_segmentation = True if settingtourney.use_segmentation and settingtourney.use_segmentation == 'YES' else False
    if db_tourney.use_segmentation != use_segmentation:
        db_tourney.use_segmentation = use_segmentation
          
    if settingtourney.limitPenaltyPoints and db_tourney.penalties_limit != int(settingtourney.limitPenaltyPoints):
        db_tourney.penalties_limit = int(settingtourney.limitPenaltyPoints)
        
    if settingtourney.points_penalty_yellow and db_tourney.points_penalty_yellow != int(settingtourney.points_penalty_yellow):
        db_tourney.points_penalty_yellow = int(settingtourney.points_penalty_yellow)
        
    if settingtourney.points_penalty_red and db_tourney.points_penalty_red != int(settingtourney.points_penalty_red):
        db_tourney.points_penalty_red = int(settingtourney.points_penalty_red)
        
    if settingtourney.constant_increase_ELO and db_tourney.constant_increase_ELO != float(settingtourney.constant_increase_ELO):
        db_tourney.constant_increase_ELO = int(settingtourney.constant_increase_ELO)
    
    use_bonus = True if settingtourney.use_bonus and settingtourney.use_bonus == 'YES' else False
    if db_tourney.use_bonus != use_bonus:
        db_tourney.use_bonus = use_bonus
        
    if use_bonus:
        if settingtourney.amount_bonus_tables and db_tourney.amount_bonus_tables != int(settingtourney.amount_bonus_tables):
            db_tourney.amount_bonus_tables = int(settingtourney.amount_bonus_tables)
        if settingtourney.amount_bonus_points and db_tourney.amount_bonus_points != int(settingtourney.amount_bonus_points):
            db_tourney.amount_bonus_points = int(settingtourney.amount_bonus_points)
            
    if settingtourney.round_ordering_one and db_tourney.round_ordering_one != str(settingtourney.round_ordering_one):
        db_tourney.round_ordering_one = str(settingtourney.round_ordering_one)
    if settingtourney.round_ordering_two and db_tourney.round_ordering_two != str(settingtourney.round_ordering_two):
        db_tourney.round_ordering_two = str(settingtourney.round_ordering_two)
    if settingtourney.round_ordering_three and db_tourney.round_ordering_three != str(settingtourney.round_ordering_three):
        db_tourney.round_ordering_three = str(settingtourney.round_ordering_three)
            
    if not db_tourney.round_ordering_one or not db_tourney.round_ordering_two or not db_tourney.round_ordering_three:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.round_ordering_incorrect"))
            
    if settingtourney.event_ordering_one and db_tourney.event_ordering_one != str(settingtourney.event_ordering_one):
        db_tourney.event_ordering_one = str(settingtourney.event_ordering_one)
    if settingtourney.event_ordering_two and db_tourney.event_ordering_two != str(settingtourney.event_ordering_two):
        db_tourney.event_ordering_two = str(settingtourney.event_ordering_two)
    if settingtourney.event_ordering_three and db_tourney.event_ordering_three != str(settingtourney.event_ordering_three):
        db_tourney.event_ordering_three = str(settingtourney.event_ordering_three)
        
    if not db_tourney.event_ordering_one or not db_tourney.event_ordering_two or not db_tourney.event_ordering_three:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.event_ordering_incorrect"))
    
    if db_tourney.name != str(settingtourney.amount_smart_tables):
        db_tourney.name = str(settingtourney.amount_smart_tables)
        
    if db_tourney.summary != str(settingtourney.summary):
        db_tourney.summary = str(settingtourney.summary)
        
    if db_tourney.start_date != settingtourney.start_date:
        db_tourney.start_date = settingtourney.start_date
        
    if db_tourney.number_rounds != int(settingtourney.number_rounds):
        db_tourney.number_rounds = int(settingtourney.number_rounds)
        
    db_tourney.updated_by=currentUser['username']
    
    update_initializes_tourney(db_tourney, locale, db=db)
    
    return result

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
    
    #pasar todos los jugadores que estén en estado jugando o en espera a confirmados para que vuelva a empezar la distribución.
    # try:
    db.add(db_tourney)
    db.commit()
    return True
       
    # except (Exception, SQLAlchemyError, IntegrityError) as e:
    #     return False