import math

from datetime import datetime
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.events import Event
from domino.schemas.events import EventBase, EventSchema
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.services.status import get_one_by_name, get_one as get_one_status
from domino.app import _
from domino.services.utils import get_result_count
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_from = "FROM events.events eve " +\
        "JOIN resources.entities_status sta ON sta.id = eve.status_id " +\
        "JOIN resources.city city ON city.id = eve.city_id"
        
    str_count = "Select count(*) " + str_from
    str_query = "Select eve.id, eve.name, start_date, close_date, registration_date, registration_price, city.name as city_name, " +\
        "main_location, summary, image, eve.status_id, sta.name as status_name " + str_from
    
    str_where = " WHERE sta.name != 'CANCELLED' "  
    
    dict_query = {'name': " AND eve.name ilike '%" + criteria_value + "%'",
                  'summary': " AND summary ilike '%" + criteria_value + "%'",
                  'city_name': " AND city_name ilike '%" + criteria_value + "%'",
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
    
    new_row = {'id': item['id'], 'name': item['name'], 
               'startDate': item['start_date'], 'endDate': item['close_date'], 
               'city': item['city_name'], 'campus': item['main_location'], 
               'summary' : item['summary'],
               'photo' : item['image']}
    if page != 0:
        new_row['selected'] = False
    return new_row

def get_one(event_id: str, db: Session):  
    return db.query(Event).filter(Event.id == event_id).first()

def get_one_by_id(event_id: str, db: Session): 
    result = ResultObject()  
    result.data = db.query(Event).filter(Event.id == event_id).first()
    return result

def new(request, db: Session, event: EventBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_status = get_one_by_name('CREATED', db=db)
    if not one_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    verify_dates(event.start_date, event.close_date, event.registration_date, locale)
    
    db_event = Event(name=event.name, summary=event.summary, start_date=event.start_date, 
                     image=event.image, close_date=event.close_date,
                     registration_date=event.registration_date, registration_price=event.registration_price,
                     city_id=event.city_id, main_location=event.main_location, status_id=one_status.id,
                     created_by=currentUser['username'], updated_by=currentUser['username'])
    
    try:
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "event.error_new_event")               
        raise HTTPException(status_code=403, detail=msg)

def verify_dates(start_date, close_date, registration_date, locale):
    
    if start_date > close_date:
        raise HTTPException(status_code=404, detail=_(locale, "event.start_date_incorrect"))
    
    if registration_date > start_date:
        raise HTTPException(status_code=404, detail=_(locale, "event.registration_date_incorrect"))
    
    return True
 
def delete(request: Request, event_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_status = get_one_by_name('CANCELLED', db=db)
    if not one_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    try:
        db_event = db.query(Event).filter(Event.id == event_id).first()
        if db_event:
            db_event.status_id = one_status.id
            db_event.updated_by = currentUser['username']
            db_event.updated_date = datetime.now()
            db.commit()
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "event.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "event.imposible_delete"))
    
def update(request: Request, event_id: str, event: EventBase, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
       
    db_event = db.query(Event).filter(Event.id == event_id).first()
    
    if db_event:
        
        if db_event.status_id == 4:  # FINALIZED
            raise HTTPException(status_code=400, detail=_(locale, "event.event_closed"))
    
        if event.name and db_event.name != event.name:
            db_event.name = event.name
        
        if event.summary and db_event.summary != event.summary:    
            db_event.summary = event.summary
            
        if event.image and db_event.image != event.image:    
            db_event.image = event.image
            
        if event.start_date and db_event.start_date != event.start_date:    
            db_event.start_date = event.start_date
            
        if event.close_date and db_event.close_date != event.close_date:    
            db_event.close_date = event.close_date
            
        if event.registration_date and db_event.registration_date != event.registration_date:    
            db_event.registration_date = event.registration_date
            
        if event.registration_price and db_event.registration_price != event.registration_price:    
            db_event.registration_price = event.registration_price
            
        if event.city_id and db_event.city_id != event.city_id:    
            db_event.city_id = event.city_id
            
        if event.main_location and db_event.main_location != event.main_location:    
            db_event.main_location = event.main_location
            
        db_event.updated_by = currentUser['username']
        db_event.updated_date = datetime.now()
                
        try:
            db.add(db_event)
            db.commit()
            db.refresh(db_event)
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail=_(locale, "event.already_exist"))
            
    else:
        raise HTTPException(status_code=404, detail=_(locale, "event.not_found"))
