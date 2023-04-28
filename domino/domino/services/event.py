import math
import uuid

from datetime import datetime
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.events import Event
from domino.models.tourney import Tourney
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
        "JOIN resources.city city ON city.id = eve.city_id " +\
        "JOIN resources.country country ON country.id = city.country_id "
        
    str_count = "Select count(*) " + str_from
    str_query = "Select eve.id, eve.name, start_date, close_date, registration_date, registration_price, city.name as city_name, " +\
        "main_location, summary, image, eve.status_id, sta.name as status_name, country.id as country_id, city.id  as city_id " + str_from
    
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
    result.data = [create_dict_row(item, page, db=db, incluye_tourney=True) for item in lst_data]
    
    return result

def create_dict_row(item, page, db: Session, incluye_tourney=False):
    
    new_row = {'id': item['id'], 'name': item['name'], 
               'startDate': item['start_date'], 'endDate': item['close_date'], 
               'country': item['country_id'], 'city': item['city_id'],
               'city_name': item['city_name'], 'campus': item['main_location'], 
               'summary' : item['summary'],
               'photo' : item['image'], 'tourney':[]}
    if page != 0:
        new_row['selected'] = False
    
    if incluye_tourney:
        new_row['tourney'] = get_lst_tourney_by_event_id(item['id'], db=db)
        
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
    
    verify_dates(event.start_date, event.close_date, locale)
    
    id = str(uuid.uuid4())
    image = "/events/" + str(currentUser['user_id']) + "/" + str(id) + "/" + str(event.image)
    
    db_event = Event(id=id, name=event.name, summary=event.summary, start_date=event.start_date, 
                     close_date=event.close_date, registration_date=event.start_date, 
                     image=image, registration_price=float(0.00), # event.registration_price,
                     city_id=event.city_id, main_location=event.main_location, status_id=one_status.id,
                     created_by=currentUser['username'], updated_by=currentUser['username'])
    
    if event.tourney:
        for item in event.tourney:
            tourney_id = str(uuid.uuid4())
            db_tourney = Tourney(id=tourney_id, event_id=id, modality=item.modality, name=item.name, 
                                 summary=item.summary, start_date=item.start_date, 
                                 status_id=one_status.id, created_by=currentUser['username'], 
                                 updated_by=currentUser['username'])
            db_event.tourney.append(db_tourney)
    
    try:
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        result.data = {'id': id}
        return result
       
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "event.error_new_event")               
        raise HTTPException(status_code=403, detail=msg)

def verify_dates(start_date, close_date, locale):
    
    if start_date > close_date:
        raise HTTPException(status_code=404, detail=_(locale, "event.start_date_incorrect"))
    
    # if registration_date > start_date:
    #     raise HTTPException(status_code=404, detail=_(locale, "event.registration_date_incorrect"))
    
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
            
        if event.image:
            image = "/events/" + str(currentUser['user_id']) + "/" + str(db_event.id) + "/" + str(event.image)
            if db_event.image != image:   
                db_event.image = image
            
        if event.start_date and db_event.start_date != event.start_date:    
            db_event.start_date = event.start_date
            
        if event.close_date and db_event.close_date != event.close_date:    
            db_event.close_date = event.close_date
            
        if event.city_id and db_event.city_id != event.city_id:    
            db_event.city_id = event.city_id
            
        if event.main_location and db_event.main_location != event.main_location:    
            db_event.main_location = event.main_location
        
        #desde la interfaz, los que no vengan borrarlos, si vienen nuevos insertarlos, si coinciden modificarlos
        str_tourney_iface = ""
        dict_tourney = {}
        for item in db_event.tourney:
            dict_tourney[item.id] = item
            
        if event.tourney:
            one_status = get_one_by_name('CREATED', db=db)
            one_status_canc = get_one_by_name('CANCELLED', db=db)
            
            for item in event.tourney:
                if not item.id:  # viene el torneo pero vacio, es nuevo
                    tourney_id = str(uuid.uuid4())
                    db_tourney = Tourney(id=tourney_id, event_id=event_id, modality=item.modality, name=item.name, 
                                        summary=item.summary, start_date=item.start_date, 
                                        status_id=one_status.id, created_by=currentUser['username'], 
                                        updated_by=currentUser['username'])
                    db_event.tourney.append(db_tourney)
                    
                else:
                    str_tourney_iface += " " + item.id
                    if item.id in dict_tourney:  # modificar datos del torneo
                        db_tourney = dict_tourney[item.id]
                        if db_tourney.status_id == 4:  # FINALIZED
                            raise HTTPException(status_code=400, detail=_(locale, "tourney.tourney_closed"))
                    
                        if item.name and db_tourney.name != item.name:
                            db_tourney.name = item.name
                        
                        if item.summary and db_tourney.summary != item.summary:    
                            db_tourney.summary = item.summary
                            
                        if item.modality and db_tourney.modality != item.modality:    
                            db_tourney.modality = item.modality
                            
                        if item.start_date and db_tourney.start_date != item.start_date:    
                            db_tourney.start_date = item.start_date
                            
                        db_tourney.updated_by = currentUser['username']
                        db_tourney.updated_date = datetime.now()
            
            for item_key, item_value in dict_tourney.items():
                if item_key not in str_tourney_iface:
                    item_value.status_id = one_status_canc.id
                
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

def get_lst_tourney_by_event_id(event_id: str, db: Session): 
    
    lst_return = []
    
    str_from = "FROM events.tourney tou " +\
        "JOIN resources.entities_status sta ON sta.id = tou.status_id "
    
    str_query = "Select tou.id, event_id, tou.modality, tou.name, tou.summary, tou.start_date, " +\
        "tou.status_id, sta.name as status_name " + str_from
    
    str_query += " WHERE sta.name != 'CANCELLED' and event_id = '" + str(event_id) + "' ORDER BY start_date "  
    lst_data = db.execute(str_query)
    lst_return = [create_dict_row_tourney(item) for item in lst_data]
    
    return lst_return

def create_dict_row_tourney(item):
    
    new_row = {'id': item['id'], 'event_id': item['event_id'], 'name': item['name'], 
               'modality': item['modality'], 'summary' : item['summary'], 'startDate': item['start_date']
               }
       
    return new_row