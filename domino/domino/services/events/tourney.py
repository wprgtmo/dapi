import math
import uuid
from typing import List
from datetime import datetime
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _

from domino.models.events.tourney import Tourney
from domino.schemas.events.tourney import TourneyBase, TourneySchema, TourneyCreated
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.status import get_one_by_name, get_one as get_one_status

from domino.services.resources.utils import get_result_count
from domino.services.events.event import get_one as get_one_event, get_all as get_all_event
            
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
    
    one_status = get_one_by_name('CREATED', db=db)
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
    
    one_status = get_one_by_name('CANCELLED', db=db)
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
    
    one_status_end = get_one_by_name('FINALIZED', db=db)
    one_status_new = get_one_by_name('CREATED', db=db)
    one_status_canc = get_one_by_name('CANCELLED', db=db)
    
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
   
def update_original(request: Request, tourney_id: str, tourney: TourneyCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    one_status_end = get_one_by_name('FINALIZED', db=db)
    one_status_new = get_one_by_name('CREATED', db=db)
    one_status_canc = get_one_by_name('CANCELLED', db=db)
    
    tourney = get_one(tourney_id, db=db)
    if tourney.status_id != one_status_new.id:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
    if tourney:
        # desde la interfaz, los que no vengan borrarlos, si vienen nuevos insertarlos, si coinciden modificarlos
        str_tourney_iface = ""
        dict_tourney = {}
        for item_to in one_event.tourney:
            dict_tourney[item_to.id] = item_to
            
        for item in tourney:
            if 'id' not in item or not item.id_tourney:  # viene el torneo pero vacio, es nuevo
                tourney_id = str(uuid.uuid4())
                db_tourney = Tourney(id=tourney_id, event_id=event_id, modality=item.modality, name=item.name, 
                                     summary=item.summary, start_date=item.startDate, 
                                     status_id=one_status_new.id, created_by=currentUser['username'],
                                     updated_by=currentUser['username'])
                one_event.tourney.append(db_tourney)
                
            else:
                str_tourney_iface += " " + item.id_tourney
                if item.id_tourney in dict_tourney:  # modificar datos del torneo
                    db_tourney = dict_tourney[item.id_tourney]
                    if db_tourney.status_id == one_status_end.id:  # FINALIZED
                        raise HTTPException(status_code=400, detail=_(locale, "tourney.tourney_closed"))
                
                    if 'name' in item and item.name and db_tourney.name != item.name:
                        db_tourney.name = item.name
                    
                    if 'summary' in item and item.summary and db_tourney.summary != item.summary:    
                        db_tourney.summary = item.summary
                        
                    if 'modality' in item and item.modality and db_tourney.modality != item.modality:    
                        db_tourney.modality = item.modality
                        
                    if 'startDate' in item and item.startDate and db_tourney.start_date != item.startDate:    
                        db_tourney.start_date = item.startDate
                        
                    db_tourney.updated_by = currentUser['username']
                    db_tourney.updated_date = datetime.now()
        
        for item_key, item_value in dict_tourney.items():
            if item_key not in str_tourney_iface:
                item_value.status_id = one_status_canc.id
        
        try:
            db.add(one_event)
            db.commit()
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail=_(locale, "tourney.already_exist"))
            
    else:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))


