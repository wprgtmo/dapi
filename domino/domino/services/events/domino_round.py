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

from domino.models.events.domino_round import DominoRounds
from domino.models.events.tourney import SettingTourney

from domino.schemas.events.events import EventBase, EventSchema
from domino.schemas.resources.result_object import ResultObject

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
from domino.services.enterprise.users import get_one_by_username
from domino.services.enterprise.userprofile import get_one as get_one_profile
                         
def get_all(request:Request, profile_id:str, tourney_id:str, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    # verificar que el perfil sea admon del evento al cual pertenece el torneo.
    db_member_profile = get_one_profile(id=profile_id, db=db)
    if not db_member_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
   
    if db_member_profile.profile_type != 'EVENTADMON':
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.user_not_event_admon"))
    
    str_from = "FROM events.domino_tables dtab " +\
        "JOIN events.tourney dtou ON dtou.id = dtab.tourney_id " +\
        "JOIN events.setting_tourney stou ON stou.tourney_id = dtou.id "  
        
    str_count = "Select count(*) " + str_from
    str_query = "Select dtab.id, table_number, is_smart, amount_bonus, dtab.image, dtab.is_active, " +\
        "dtou.id as tourney_id, dtou.name, stou.image as image_tourney " + str_from
    
    str_where = " WHERE dtab.tourney_id = '" + tourney_id + "' "  
    
    dict_query = {'table_number': " AND table_number = " + criteria_value}
    
    str_count += str_where
    str_query += str_where
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY table_number " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, tourney_id, page, db=db, api_uri=api_uri) for item in lst_data]
    
    return result

def create_dict_row(item, tourney_id, page, db: Session, api_uri=""):
    
    image_name = item['image'] if item['image'] else item['image_tourney']
    image = api_uri + "/api/public/advertising/" + str(item['tourney_id']) + "/" + image_name
    
    new_row = {'id': item['id'], 'table_number': item['table_number'], 
               'is_smart': item['is_smart'], 'amount_bonus': item['amount_bonus'], 
               'tourney_name': item['name'], 'is_active': item['is_active'],
               'photo' : image, 'filetables':[]}
    if page != 0:
        new_row['selected'] = False
        
    if item['is_smart']:
        str_files = "Select id, position, is_ready from events.files_tables Where table_id = '" + item['id'] + "' "
        lst_files = db.execute(str_files)
        for item_f in lst_files:
            new_row['filetables'].append({'file_id': item_f.id, 'position': item_f.position, 'is_ready': item_f.is_ready})
    
    return new_row

def get_one(round_id: str, db: Session):  
    return db.query(DominoRounds).filter(DominoRounds.id == round_id).first()

def get_one_by_id(round_id: str, db: Session): 
    result = ResultObject()  
    
    one_round = get_one(round_id, db=db)
    if not one_round:
        raise HTTPException(status_code=404, detail="dominoround.not_found")
    
    str_query = "SELECT dtab.id, dtab.tourney_id, table_number, is_smart, amount_bonus, dtab.image, dtab.is_active, tourney.name " +\
        "FROM events.domino_tables dtab " + \
        "Join events.tourney ON tourney.id = dtab.tourney_id " +\
        " WHERE dtab.id = '" + str(round_id) + "' "  
    lst_data = db.execute(str_query) 
    
    for item in lst_data: 
        result.data = [create_dict_row(item, one_round.tourney_id, 0, db=db) for item in lst_data]
        
    if not result.data:
        raise HTTPException(status_code=404, detail="dominoround.not_found")
    
    return result

def configure_new_rounds(db_tourney, summary:str, db:Session, created_by:str):
  
    str_number = "SELECT round_number FROM events.domino_rounds where tourney_id = '" + db_tourney.id + "' " +\
        "ORDER BY round_number DESC LIMIT 1; "
    last_number = db.execute(str_number).fetchone()
    
    round_number = 1 if not last_number else int(last_number) + 1
    
    status_creat = get_one_status_by_name('CREATED', db=db)
    
    id = str(uuid.uuid4())
    db_round = DominoRounds(id=id, tourney_id=db_tourney.id, round_number=round_number, summary=summary,
                            start_date=datetime.now(), close_date=datetime.now(), created_by=created_by, 
                            updated_by=created_by, created_date=datetime.now(), updated_date=datetime.now(),
                            status_id=status_creat.id)
    
    try:
        db.add(db_round)
        db.commit()
        return True
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return False
    
def delete(request: Request, round_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_round = get_one(round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "dominoround.not_found"))
    
    status_canc = get_one_status_by_name('CANCELLED', db=db)
        
    change_status_round(db_round, status_canc, currentUser['username'], db=db)
    
    return result

def start_round(request: Request, round_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    db_round = get_one(round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "dominoround.not_found"))
    
    status_init = get_one_status_by_name('INITIADED', db=db)
    
    change_status_round(db_round, status_init, currentUser['username'], db=db)
    
    return result

def close_round(request: Request, round_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    db_round = get_one(round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "dominoround.not_found"))
    
    status_init = get_one_status_by_name('FINALIZED', db=db)
    
    change_status_round(db_round, status_init, currentUser['username'], db=db)
    
    return result
            
def change_status_round(db_round, status, username, db: Session):
    
    db_round.sttaus_id = status.id
    db_round.updated_by = username
    db_round.updated_date = datetime.now()
            
    try:
        db.add(db_round)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        return False
