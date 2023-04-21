import math
import uuid

from datetime import datetime
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.tourney import Tourney
from domino.schemas.tourney import TourneyBase, TourneySchema
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.services.status import get_one_by_name, get_one as get_one_status
from domino.app import _
from domino.services.utils import get_result_count
from domino.services.event import get_one as get_one_event
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_from = "FROM events.tourney tou " +\
        "JOIN events.events eve ON eve.id = tou.event_id " +\
        "JOIN resources.entities_status sta ON sta.id = tou.status_id " +\
        "JOIN enterprise.users us ON us.id = tou.manage_id "
    
    str_count = "Select count(*) " + str_from
    str_query = "Select tou.id, event_id, eve.name as event_name, tou.modality, tou.name, tou.summary, tou.start_date, tou.close_date, " +\
        "tou.status_id, tou.image, tou.manage_id,sta.name as status_name, us.first_name || ' ' || us.last_name as full_name " + str_from
    
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
               'modality': item['modality'], 'summary' : item['summary'], 'photo' : item['image'],
               'startDate': item['start_date'], 'endDate': item['close_date'], 
               'manage_user': item['full_name'] 
               }
       
    if page != 0:
        new_row['selected'] = False
    return new_row

def get_one(tourney_id: str, db: Session):  
    return db.query(Tourney).filter(Tourney.id == tourney_id).first()

def get_one_by_id(tourney_id: str, db: Session): 
    result = ResultObject()  
    result.data = db.query(Tourney).filter(Tourney.id == tourney_id).first()
    return result

def get_all_by_event_id(event_id: str, db: Session): 
    result = ResultObject()  
    
    str_from = "FROM events.tourney tou " +\
        "JOIN events.events eve ON eve.id = tou.event_id " +\
        "JOIN resources.entities_status sta ON sta.id = tou.status_id " +\
        "LEFT JOIN enterprise.users us ON us.username = tou.manage_id "
    
    str_query = "Select tou.id, event_id, eve.name as event_name, tou.modality, tou.name, tou.summary, tou.start_date, tou.close_date, " +\
        "tou.status_id, tou.image, tou.manage_id,sta.name as status_name, us.first_name || ' ' || us.last_name as full_name " + str_from
    
    str_query += " WHERE sta.name != 'CANCELLED' and event_id = '" + str(event_id) + "' ORDER BY start_date "  
    print (str_query)
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, 0, db=db) for item in lst_data]
    
    return result

def new(request, db: Session, tourney: TourneyBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_status = get_one_by_name('CREATED', db=db)
    if not one_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    verify_dates(tourney.start_date, tourney.close_date, locale)
    
    id = str(uuid.uuid4())
    image = "/events/tourney/" + str(currentUser['user_id']) + "/" + str(id) + "/" + str(tourney.image)
    
    one_event = get_one_event(tourney.event_id, db=db)
    if one_event.status_id != one_status.id:
        raise HTTPException(status_code=404, detail=_(locale, "event.event_closed"))
    
    manage_id = tourney.manage_id if tourney.manage_id else currentUser['username']
    
    db_tourney = Tourney(id=id, event_id=tourney.event_id, modality=tourney.modality, name=tourney.name, 
                         summary=tourney.summary, start_date=tourney.start_date, 
                         close_date=tourney.close_date, image=image, manage_id=manage_id, 
                         status_id=one_status.id, created_by=currentUser['username'], 
                         updated_by=currentUser['username'])
    
    try:
        db.add(db_tourney)
        db.commit()
        db.refresh(db_tourney)
        result.data = {'tourney_id': id}
        return result
       
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "tourney.error_new_tourney")               
        raise HTTPException(status_code=403, detail=msg)

def verify_dates(start_date, close_date, locale):
    
    if start_date > close_date:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.start_date_incorrect"))
    
    return True
 
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
    
def update(request: Request, tourney_id: str, tourney: TourneyBase, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
       
    db_tourney = db.query(Tourney).filter(Tourney.id == tourney_id).first()
    
    if db_tourney:
        
        if db_tourney.status_id == 4:  # FINALIZED
            raise HTTPException(status_code=400, detail=_(locale, "tourney.tourney_closed"))
    
        if tourney.name and db_tourney.name != tourney.name:
            db_tourney.name = tourney.name
        
        if tourney.summary and db_tourney.summary != tourney.summary:    
            db_tourney.summary = tourney.summary
            
        if tourney.modality and db_tourney.modality != tourney.modality:    
            db_tourney.modality = tourney.modality
            
        if tourney.image and db_tourney.image != tourney.image:    
            db_tourney.image = tourney.image
            
        if tourney.start_date and db_tourney.start_date != tourney.start_date:    
            db_tourney.start_date = tourney.start_date
            
        if tourney.close_date and db_tourney.close_date != tourney.close_date:    
            db_tourney.close_date = tourney.close_date
            
        if tourney.manage_id and db_tourney.manage_id != tourney.manage_id:    
            db_tourney.manage_id = tourney.manage_id
            
        db_tourney.updated_by = currentUser['username']
        db_tourney.updated_date = datetime.now()
         
        try:
            db.add(db_tourney)
            db.commit()
            db.refresh(db_tourney)
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail=_(locale, "tourney.already_exist"))
            
    else:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
