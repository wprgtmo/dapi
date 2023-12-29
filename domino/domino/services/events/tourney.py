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
from domino.config.config import settings

from domino.models.events.tourney import Tourney, DominoCategory

from domino.schemas.events.tourney import TourneyCreated, SettingTourneyCreated, DominoCategoryCreated
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status

from domino.services.resources.utils import get_result_count
from domino.services.events.event import get_one as get_one_event, get_all as get_all_event

from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir, copy_image, del_image
from domino.services.enterprise.userprofile import get_one as get_one_profile
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_from = "FROM events.tourney tou " +\
        "JOIN events.events eve ON eve.id = tou.event_id " +\
        "JOIN resources.entities_status sta ON sta.id = tou.status_id " 
    
    str_count = "Select count(*) " + str_from
    str_query = "Select tou.id, event_id, eve.name as event_name, tou.modality, tou.name, tou.summary, tou.start_date, " +\
        "tou.status_id, sta.name as status_name, sta.description as status_description, lottery_type, number_rounds, image " + str_from
    
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
               'modality': item['modality'], 'summary' : item['summary'], 'startDate': item['start_date'],
               'status_id': item['status_id'], 'status_name': item['status_name'], 'status_description': item['status_description'],
               'lottery_type': item['lottery_type'], 'number_rounds': item['number_rounds']
               }
       
    if page != 0:
        new_row['selected'] = False
    return new_row

def get_one(tourney_id: str, db: Session):  
    return db.query(Tourney).filter(Tourney.id == tourney_id).first()

def get_one_by_name(tourney_name: str, db: Session):  
    return db.query(Tourney).filter(Tourney.name == tourney_name).first()

# def get_setting_tourney(tourney_id: str, db: Session):  
#     return db.query(SettingTourney).filter(SettingTourney.tourney_id == tourney_id).first()

# def get_setting_tourney_to_interface(tourney_id: str, db: Session):  
#     one_setting = get_setting_tourney(tourney_id=tourney_id, db=db)
#     return one_setting.__dict__ if one_setting else None

def get_one_by_id(tourney_id: str, db: Session): 
    result = ResultObject()  
    
    api_uri = str(settings.api_uri)
    
    str_query = "Select tou.id, event_id, eve.name as event_name, tou.modality, tou.name, tou.summary, tou.start_date, " +\
        "lottery_type, image, " +\
        "tou.status_id, sta.name as status_name, sta.description as status_description FROM events.tourney tou " +\
        "JOIN events.events eve ON eve.id = tou.event_id " +\
        "JOIN resources.entities_status sta ON sta.id = tou.status_id " +\
        " WHERE tou.id = '" + str(tourney_id)  + "' "
        
    lst_data = db.execute(str_query)
    if lst_data:
        for item in lst_data:
            result.data = create_dict_row(item, 0, db=db)
            
    result.data['amount_player'] = get_count_players_by_tourney(tourney_id, result.data['modality'], db=db)
    
    return result

def get_count_players_by_tourney(tourney_id: str, modality: str, db: Session):  
    
    dict_modality = {'Individual': "join enterprise.profile_single_player player ON player.profile_id = pro.id ",
                     'Parejas': "join enterprise.profile_pair_player player ON player.profile_id = pro.id ",
                     'Equipo': "join enterprise.profile_team_player player ON player.profile_id = pro.id "}
    
    str_query = "Select count(*) FROM events.players " +\
        "inner join enterprise.profile_member pro ON pro.id = players.profile_id " +\
        "inner join enterprise.profile_type prot ON prot.name = pro.profile_type "
    
    str_query += dict_modality[modality]
    
    str_query += "WHERE pro.is_ready is True " +\
        " AND players.tourney_id = '" + tourney_id + "' " 
    
    amount_player = db.execute(str_query).scalar()
    
    return amount_player

def get_all_by_event_id(event_id: str, db: Session): 
    result = ResultObject()  
    
    str_from = "FROM events.tourney tou " +\
        "JOIN events.events eve ON eve.id = tou.event_id " +\
        "JOIN resources.entities_status sta ON sta.id = tou.status_id "
    
    str_query = "Select tou.id, event_id, eve.name as event_name, tou.modality, tou.name, tou.summary, tou.start_date, " +\
        "tou.status_id, sta.name as status_name, lottery_type, number_rounds, image " + str_from
    
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
    
    one_status_end = get_one_status_by_name('FINALIZED', db=db)
    if not one_status_end:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    one_event = get_one_event(event_id, db=db)
    if one_event.status_id == one_status_end.id:
        raise HTTPException(status_code=404, detail=_(locale, "event.event_closed"))
    
    id = str(uuid.uuid4())
    if tourney.startDate < one_event.start_date: 
        raise HTTPException(status_code=404, detail=_(locale, "tourney.incorrect_startDate"))
    
    if tourney.startDate > one_event.close_date: 
        raise HTTPException(status_code=404, detail=_(locale, "tourney.incorrect_startDate"))
    
    db_tourney = Tourney(id=id, event_id=event_id, modality=tourney.modality, name=tourney.name, 
                         summary=tourney.summary, start_date=tourney.startDate, 
                         status_id=one_status.id, created_by=currentUser['username'], 
                         game_system='SUIZO', number_rounds=tourney.number_rounds,
                         updated_by=currentUser['username'], profile_id=one_event.profile_id)
    db.add(db_tourney)
    
    #crear la carpeta con la imagen de la publicidad....
    path = create_dir(entity_type="SETTOURNEY", user_id=None, entity_id=str(db_tourney.id))
    
    image_domino="public/smartdomino.png"
    image_destiny = path + "smartdomino.png"
    copy_image(image_domino, image_destiny)
        
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

def update_image_tourney(request: Request, tourney_id: str, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    one_status_end = get_one_status_by_name('FINALIZED', db=db)
    
    db_tourney = get_one(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    if db_tourney.status_id == one_status_end.id:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
    db_tourney.updated_by = currentUser['username']
    db_tourney.updated_date = datetime.now()
    
    path_tourney = create_dir(entity_type="SETTOURNEY", user_id=None, entity_id=str(db_tourney.id))
    
    #puede venir la foto o no venir y eso es para borrarla.
    if db_tourney.image:  # ya tiene una imagen asociada
        current_image = db_tourney.image
        try:
            del_image(path=path_tourney, name=str(current_image))
        except:
            pass
    
    if not file:
        db_tourney.image = None
    else:   
        ext = get_ext_at_file(file.filename)
        file.filename = str(uuid.uuid4()) + "." + ext
        
        upfile(file=file, path=path_tourney)
        db_tourney.image = file.filename
    
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
    
    str_query = "Select count(*) From events.players Where is_active = True and tourney_id = '" + tourney_id + "' "
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
    
    amount_table = int(mod_play[0]) if mod_play[1] > 0 else int(mod_play[0])
    return amount_table

def calculate_elo_by_tourney(tourney_id: str, modality:str, db: Session):
    
    str_query = "Select count(*) From events.players Where is_active = True and tourney_id = '" + tourney_id + "' "
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

def initializes_tourney(tourney_id, amount_tables, amount_smart_tables, amount_rounds, number_points_to_win, 
                        time_to_win, game_system, use_bonus, lottery_type, penalties_limit, db: Session):
    
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
    
    sett_tourney.tourney_id = tourney_id
    
    try:
        db.add(sett_tourney)
        db.commit()
        return True
       
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return False
    
def init_setting(tourney_id, modality, db: Session):
    
    amount_tables = calculate_amount_tables(tourney_id, modality=modality, db=db)
    elo_max, elo_min = get_values_elo_by_tourney(tourney_id=tourney_id, modality=modality, db=db)
    
    sett_tourney = SettingTourney(
        amount_tables=amount_tables, amount_smart_tables=0, amount_rounds=0, use_bonus=False, amount_bonus_tables=0, 
        amount_bonus_points=0, number_bonus_round=0, number_points_to_win=0, time_to_win=0, 
        game_system='', lottery_type='', penalties_limit=0, elo_min=elo_min, elo_max=elo_max, image='')
    
    sett_tourney.tourney_id = tourney_id
    
    try:
        db.add(sett_tourney)
        db.commit()
        return sett_tourney
       
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return None
    
def update_initializes_tourney(one_setting, amount_smart_tables, amount_rounds, number_points_to_win, 
                        time_to_win, game_system, use_bonus, lottery_type, penalties_limit, db: Session):
    
    divmod_round = divmod(amount_rounds,5)
    
    one_setting.amount_smart_tables = amount_smart_tables
    one_setting.amount_rounds = amount_rounds
    one_setting.use_bonus = use_bonus
    one_setting.amount_bonus_tables = amount_rounds // 4 
    one_setting.amount_bonus_points = (amount_rounds // 4) * 2
    one_setting.number_bonus_round = amount_rounds + 1 if amount_rounds <= 9 else 4 if amount_rounds <= 15 else \
        divmod_round[0] if divmod_round[1] == 0 else divmod_round[0] + 1
    one_setting.number_points_to_win = number_points_to_win
    
    one_setting.time_to_win = time_to_win
    one_setting.game_system = game_system
    one_setting.lottery_type = lottery_type
    one_setting.penalties_limit = penalties_limit
    
    try:
        db.add(one_setting)
        db.commit()
        return True
       
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return False
   
def configure_one_tourney(request, tourney_id: str, settingtourney: SettingTourneyCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_status_new = get_one_status_by_name('CREATED', db=db)
    
    db_tourney = get_one(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    if db_tourney.status_id != one_status_new.id:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
    amount_tables = calculate_amount_tables(db_tourney.id, db_tourney.modality, db=db)
    
    try:
        amount_smart_tables = int(settingtourney['amount_smart_tables'])
        amount_rounds = int(settingtourney['amount_rounds'])
        number_points_to_win = int(settingtourney['number_points_to_win'])
        time_to_win = int(settingtourney['time_to_win'])
        game_system = str(settingtourney['game_system'])
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
    
    time_to_win = 12 if not time_to_win else time_to_win
    
    one_settingtourney = get_setting_tourney(db_tourney.id, db=db)
    if not one_settingtourney:
        initializes_tourney(
            tourney_id, amount_tables, amount_smart_tables, amount_rounds, number_points_to_win, time_to_win, game_system, 
            use_bonus, lottery_type, penalties_limit, db=db)
    else:
        update_initializes_tourney(one_settingtourney, amount_smart_tables, amount_rounds, number_points_to_win, 
                                   time_to_win, game_system, use_bonus, lottery_type, penalties_limit, db=db)
    
    return result

def configure_categories_tourney(request, tourney_id: str, lst_categories: List[DominoCategoryCreated], db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    db_tourney = get_one(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
   
    status_created = get_one_status_by_name('CREATED', db=db)
    
    if db_tourney.status_id != status_created.id:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.is_configurated"))
    
    str_query = "SELECT count(tourney_id) FROM events.domino_categories where tourney_id = '" + tourney_id + "' "
    amount = db.execute(str_query).fetchone()[0]
    if amount > 0:  #borrar todo lo que esta salvado y poner siempre nuevo...
        str_delete = "DELETE FROM events.domino_categories Where tourney_id = '" + tourney_id + "'; COMMIT; "
        db.execute(str_delete)
    
    position_number = 0
    for item in lst_categories:
        position_number += 1
        db_one_category = DominoCategory(id=str(uuid.uuid4()), tourney_id=tourney_id, category_number=item.category_number,
                                         position_number=position_number, elo_min=item.elo_min, elo_max=item.elo_max) 
        db.add(db_one_category)
    
    try:
        db.commit()
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return result

def get_all_categories_tourney(request:Request, tourney_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    result.data = get_list_categories_tourney(tourney_id=tourney_id, db=db)
    if not result.data:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.categories_not_exist"))
        
    return result

def get_list_categories_tourney(tourney_id: str, db: Session):
    
    str_query = "SELECT * FROM events.domino_categories where tourney_id = '" + tourney_id + "' ORDER BY position_number"
    lst_cat = db.execute(str_query).fetchall()
    lst_data = []
    for item in lst_cat:
        lst_data.append({'id': item.id, 'category_number': item.category_number, 'elo_min': item.elo_min, 'elo_max': item.elo_max})
    
    return lst_data

def get_info_categories_tourney(category_id: str, db: Session):
    
    str_query = "SELECT cat.id, cat.tourney_id, tourney.modality, cat.elo_min, cat.elo_max, tourney.lottery_type, st.name as status_name " +\
        "FROM events.domino_categories cat JOIN events.tourney ON " +\
        "tourney.id = cat.tourney_id JOIN resources.entities_status st ON st.id = tourney.status_id " +\
        "where cat.id = '" + category_id + "' "
    lst_cat = db.execute(str_query).fetchall()
    
    dict_result = {}
    for item in lst_cat:
        dict_result = {'id': item.id, 'tourney_id': item.tourney_id, 'modality': item.modality, 
                       'elo_min': item.elo_min, 'elo_max': item.elo_max, 'lottery_type': item.lottery_type,
                       'status_name': item.status_name}
    
    return dict_result

def get_one_domino_category(category_id: str, db: Session):
    return db.query(DominoCategory).filter(DominoCategory.id == category_id).first()
    
def save_image_tourney(request, tourney_id: str, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    db_tourney = get_one(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    path = create_dir(entity_type="SETTOURNEY", user_id=None, entity_id=str(db_tourney.id))
    
    # si torneo tiene imagen ya, eliminarla primero
    if db_tourney.image:
        try:
            del_image(path, db_tourney.image)
        except:
            pass
    
    image_id=str(uuid.uuid4())
    if file:
        ext = get_ext_at_file(file.filename)
        file.filename = str(image_id) + "." + ext
        db_tourney.image = file.filename
        upfile(file=file, path=path)
    else:
        image_domino="public/smartdomino.png"
        filename = str(image_id) + ".png"
        image_destiny = path + filename
        copy_image(image_domino, image_destiny)
        db_tourney.image = filename
     
    try:
        db.add(db_tourney)
        
        db.commit()
        return result
        
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return result
 
    return result
   
def get_values_elo_by_tourney(tourney_id: str, modality:str, db: Session):  
    
    str_from = "FROM events.players " +\
        "inner join enterprise.profile_member pro ON pro.id = players.profile_id " +\
        "inner join enterprise.profile_type prot ON prot.name = pro.profile_type " 
    
    dict_modality = {'Individual': "join enterprise.profile_single_player player ON player.profile_id = pro.id ",
                     'Parejas': "join enterprise.profile_pair_player player ON player.profile_id = pro.id ",
                     'Equipo': "join enterprise.profile_team_player player ON player.profile_id = pro.id "}
    
    str_from += dict_modality[modality]
       
    str_query = "SELECT MAX(elo) elo_max, MIN(elo) elo_min " + str_from
    
    str_where = "WHERE pro.is_ready is True and players.is_active is True " 
    str_where += " AND players.tourney_id = '" + tourney_id + "' "  
    
    str_query += str_where

    lst_data = db.execute(str_query)
    elo_max, elo_min = float(0.00), float(0.00)
    for item in lst_data:
        elo_max = item.elo_max
        elo_min = item.elo_min
    
    return elo_max, elo_min