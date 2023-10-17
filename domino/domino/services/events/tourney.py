import math
import uuid
from typing import List
from datetime import datetime
from fastapi import HTTPException, Request, File
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _

from domino.models.events.tourney import Tourney, SettingTourney
from domino.schemas.events.tourney import TourneyBase, TourneySchema, TourneyCreated, SettingTourneyCreated
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status

from domino.services.resources.utils import get_result_count
from domino.services.events.event import get_one as get_one_event, get_all as get_all_event

from domino.services.events.domino_table import configure_domino_tables
from domino.services.events.domino_round import configure_new_rounds

from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
from domino.services.enterprise.userprofile import get_one as get_one_profile
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_from = "FROM events.tourney tou " +\
        "JOIN events.events eve ON eve.id = tou.event_id " +\
        "JOIN resources.entities_status sta ON sta.id = tou.status_id " 
    
    str_count = "Select count(*) " + str_from
    str_query = "Select tou.id, event_id, eve.name as event_name, tou.modality, tou.name, tou.summary, tou.start_date, " +\
        "tou.status_id, sta.name as status_name " + str_from
    
    str_where = " WHERE sta.name != 'CANCELLED' "  
    
    dict_query = {'name': " AND eve.name ilike '%" + criteria_value + "%'",
                  'summary': " AND summary ilike '%" + criteria_value + "%'",
                  'modality': " AND modality ilike '%" + criteria_value + "%'",
                  'start_date': " AND start_date >= '%" + criteria_value + "%'",
                  }
    
    str_count += str_where
    str_query += str_where
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY start_date " 
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db) for item in lst_data]
    
    return result

def create_dict_row(item, page, db: Session):
    
    new_row = {'id': item['id'], 'event_id': item['event_id'], 'event_name': item['event_name'], 'name': item['name'], 
               'modality': item['modality'], 'summary' : item['summary'], 'startDate': item['start_date'] 
               }
       
    if page != 0:
        new_row['selected'] = False
    return new_row

def get_one(tourney_id: str, db: Session):  
    return db.query(Tourney).filter(Tourney.id == tourney_id).first()

def get_one_by_name(tourney_name: str, db: Session):  
    return db.query(Tourney).filter(Tourney.name == tourney_name).first()

def get_setting_tourney(tourney_id: str, db: Session):  
    return db.query(SettingTourney).filter(SettingTourney.tourney_id == tourney_id).first()

def get_one_by_id(tourney_id: str, db: Session): 
    result = ResultObject()  
    str_query = "Select tou.id, event_id, eve.name as event_name, tou.modality, tou.name, tou.summary, tou.start_date, " +\
        "tou.status_id, sta.name as status_name FROM events.tourney tou " +\
        "JOIN events.events eve ON eve.id = tou.event_id " +\
        "JOIN resources.entities_status sta ON sta.id = tou.status_id " +\
        " WHERE tou.id = '" + str(tourney_id)  + "' "
        
    lst_data = db.execute(str_query)
    if lst_data:
        for item in lst_data:
            result.data = create_dict_row(item, 0, db=db)
            
    # incluir los datos del setting del torneo
    setting = get_setting_tourney(tourney_id, db=db)
    if setting:
        result.data['setting'] = setting
        
    return result

def get_all_by_event_id(event_id: str, db: Session): 
    result = ResultObject()  
    
    str_from = "FROM events.tourney tou " +\
        "JOIN events.events eve ON eve.id = tou.event_id " +\
        "JOIN resources.entities_status sta ON sta.id = tou.status_id "
    
    str_query = "Select tou.id, event_id, eve.name as event_name, tou.modality, tou.name, tou.summary, tou.start_date, " +\
        "tou.status_id, sta.name as status_name " + str_from
    
    str_query += " WHERE sta.name != 'CANCELLED' and event_id = '" + str(event_id) + "' ORDER BY start_date "  
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, 0, db=db) for item in lst_data]
    
    return result

def new(request, event_id: str, tourney: TourneyCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_status = get_one_status_by_name('CREATED', db=db)
    if not one_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    one_event = get_one_event(event_id, db=db)
    if one_event.status_id != one_status.id:
        raise HTTPException(status_code=404, detail=_(locale, "event.event_closed"))
    
    id = str(uuid.uuid4())
    if tourney.startDate < one_event.start_date: 
        raise HTTPException(status_code=404, detail=_(locale, "tourney.incorrect_startDate"))
    
    if tourney.startDate > one_event.close_date: 
        raise HTTPException(status_code=404, detail=_(locale, "tourney.incorrect_startDate"))
    
    db_tourney = Tourney(id=id, event_id=event_id, modality=tourney.modality, name=tourney.name, 
                         summary=tourney.summary, start_date=tourney.startDate, 
                         status_id=one_status.id, created_by=currentUser['username'], 
                         updated_by=currentUser['username'], profile_id=one_event.profile_id)
    db.add(db_tourney)
    
    try:
        
        db.commit()
        result.data = {'event_id': event_id}
        return result
       
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "tourney.error_new_tourney")               
        raise HTTPException(status_code=403, detail=msg)

def delete(request: Request, tourney_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_status = get_one_status_by_name('CANCELLED', db=db)
    if not one_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    try:
        db_tourney= db.query(Tourney).filter(Tourney.id == tourney_id).first()
        if db_tourney:
            db_tourney.status_id = one_status.id
            db_tourney.updated_by = currentUser['username']
            db_tourney.updated_date = datetime.now()
            db.commit()
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "tourney.imposible_delete"))
    
def update(request: Request, tourney_id: str, tourney: TourneyCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    one_status_end = get_one_status_by_name('FINALIZED', db=db)
    one_status_new = get_one_status_by_name('CREATED', db=db)
    one_status_canc = get_one_status_by_name('CANCELLED', db=db)
    
    db_tourney = get_one(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    if db_tourney.status_id != one_status_new.id:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
    if db_tourney.name != tourney.name:
        db_tourney.name = tourney.name
        
    if db_tourney.summary != tourney.summary:
        db_tourney.summary = tourney.summary
        
    if db_tourney.modality != tourney.modality:
        db_tourney.modality = tourney.modality
        
    if db_tourney.start_date != tourney.startDate:
        db_tourney.start_date = tourney.startDate
        
    db_tourney.updated_by = currentUser['username']
    db_tourney.updated_date = datetime.now()
    
    try:
        db.add(db_tourney)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "tourney.already_exist"))
   
def get_amount_tables(request: Request, tourney_id: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()
    
    db_tourney = get_one(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    result.data = calculate_amount_tables(tourney_id, db_tourney.modality, db=db)
    
    return result

def calculate_amount_tables(tourney_id: str, modality: str, db: Session):
    
    str_query = "Select count(*) From events.players Where tourney_id = '" + tourney_id + "' "
    amount_players = db.execute(str_query).fetchone()[0]
    
    if amount_players == 0:
        return int(0)
    
    if modality == 'Individual':
        mod_play = divmod(int(amount_players),4) 
    elif modality == 'Parejas':
        mod_play = divmod(int(amount_players),2) 
    elif modality == 'Equipo':
        mod_play = divmod(int(amount_players),2) 
    
    if not mod_play:
        return int(0)
    
    return int(mod_play[0]) + 1 if mod_play[1] > 0 else int(mod_play[0])

def initializes_tourney(db_tourney, amount_tables, amount_smart_tables, amount_rounds, number_points_to_win, 
                        time_to_win, game_system, use_bonus, lottery_type, penalties_limit, 
                        status_init, created_by, file: File, db: Session):
    
    if file:
        ext = get_ext_at_file(file.filename)
        file.filename = str(db_tourney.id) + "." + ext
        
        path = create_dir(entity_type="SETTOURNEY", user_id=None, entity_id=str(db_tourney.id))
    
    amount_bonus_tables = amount_rounds // 4 
    divmod_round = divmod(amount_rounds,5)
    number_bonus_round = amount_rounds + 1 if amount_rounds <= 9 else 4 if amount_rounds <= 15 else \
        divmod_round[0] if divmod_round[1] == 0 else divmod_round[0] + 1
    amount_bonus_points = amount_bonus_tables * 2
    
    sett_tourney = SettingTourney(amount_tables=amount_tables, amount_smart_tables=amount_smart_tables, 
                                  amount_rounds=amount_rounds, use_bonus=use_bonus,
                                  amount_bonus_tables=amount_bonus_tables, amount_bonus_points=amount_bonus_points, 
                                  number_bonus_round=number_bonus_round, 
                                  number_points_to_win=number_points_to_win, time_to_win=time_to_win, 
                                  game_system=game_system, lottery_type=lottery_type, penalties_limit=penalties_limit)
    
    sett_tourney.tourney_id = db_tourney.id
    sett_tourney.image = file.filename if file else None
    db_tourney.status_id = status_init.id
    db_tourney.updated_by = created_by
    
    try:
        if file:
            upfile(file=file, path=path)
            
        db.add(sett_tourney)
        db.add(db_tourney)
        
        db.commit()
        return True
       
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return False
        
def configure_one_tourney(request, profile_id:str, tourney_id: str, settingtourney: SettingTourneyCreated, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    # verificar si el profile es admon de eventos
    db_member_profile = get_one_profile(id=profile_id, db=db)
    if not db_member_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
   
    if db_member_profile.profile_type != 'EVENTADMON':
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.user_not_event_admon"))
    
    one_status_init = get_one_status_by_name('INITIADED', db=db)
    one_status_new = get_one_status_by_name('CREATED', db=db)
    
    str_query = "SELECT count(tourney_id) FROM events.setting_tourney where tourney_id = '" + tourney_id + "' "
    amount = db.execute(str_query).fetchone()[0]
    if amount > 0:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.is_configurated"))
    
    db_tourney = get_one(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    if db_tourney.status_id != one_status_new.id:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
    amount_tables = calculate_amount_tables(db_tourney.id, db_tourney.modality, db=db)
    
    # try:
    amount_smart_tables = int(settingtourney['amount_smart_tables'])
    amount_rounds = int(settingtourney['amount_rounds'])
    number_points_to_win = int(settingtourney['number_points_to_win'])
    time_to_win = int(settingtourney['time_to_win'])
    game_system = str(settingtourney['game_system'])
    lottery_type = str(settingtourney['lottery'])
    penalties_limit = int(settingtourney['limitPenaltyPoints'])
    use_bonus = True if str(settingtourney['bonus']) == 'YES' else False 
        
    # except:
    #     raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_incorrect"))
    
    if amount_smart_tables > amount_tables:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.smarttable_incorrect"))
    
    result_init = initializes_tourney(
        db_tourney, amount_tables, amount_smart_tables, amount_rounds, number_points_to_win, time_to_win, game_system, 
        use_bonus, lottery_type, penalties_limit, one_status_init, currentUser['username'], file=file, db=db)
    
    if not result_init:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_tourney_failed"))
    
    one_settingtourney = get_setting_tourney(db_tourney.id, db=db)
    if not one_settingtourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_tourney_failed"))
      
    # crear las mesas y sus ficheros
    result_init = configure_domino_tables(
        db_tourney, one_settingtourney, db, currentUser['username'], file=file)
    if not result_init:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_tables_failed"))
    
    # crear la primera ronda
    result_init = configure_new_rounds(db_tourney, 'Ronda Inicial del Torneo', db=db, created_by=currentUser['username'])
    if not result_init:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_rounds_failed"))
    
    # distribuir aleatoriamente los jugadores, esto se hace en el sorteo
    
    return result
    
    
