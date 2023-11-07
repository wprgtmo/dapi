import math
import uuid

from datetime import datetime, timedelta, date
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

from domino.models.events.events import Event, EventsFollowers
from domino.models.events.tourney import Tourney

from domino.schemas.events.tourney import TourneyCreated
from domino.schemas.events.events import EventBase, EventSchema, EventFollowers
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.enterprise.users import get_one_by_username

from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir, copy_image
from domino.services.enterprise.userprofile import get_one as get_one_profile, get_one_profile_by_user, get_one_default_user
            
def get_all(request:Request, profile_id:str, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    str_from = "FROM events.events eve " +\
        "JOIN resources.entities_status sta ON sta.id = eve.status_id " +\
        "JOIN resources.city city ON city.id = eve.city_id " +\
        "JOIN resources.country country ON country.id = city.country_id " 
        
    str_count = "Select count(*) " + str_from
    str_query = "Select eve.id, eve.name, start_date, close_date, registration_date, registration_price, city.name as city_name, " +\
        "main_location, summary, image, eve.status_id, sta.name as status_name, country.id as country_id, city.id  as city_id, " +\
        "eve.profile_id as profile_id " + str_from
    
    str_where = " WHERE sta.name != 'CANCELLED' "  
    
    if profile_id:
        str_where += "AND profile_id = '" + profile_id + "' "
    
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
    
    str_query += " ORDER BY start_date DESC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db, incluye_tourney=True, api_uri=api_uri) for item in lst_data]
    
    return result

def get_all_by_criteria(request:Request, profile_id:str, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    # devolver los eventos por los criterios: Ubicación, fecha, siguiendo y participando..
    
    str_from = "FROM events.events eve " +\
        "JOIN resources.entities_status sta ON sta.id = eve.status_id " +\
        "JOIN resources.city city ON city.id = eve.city_id " +\
        "JOIN resources.country country ON country.id = city.country_id " 
        
    str_count = "Select count(*) " + str_from
    str_query = "Select eve.id, eve.name, start_date, close_date, registration_date, registration_price, city.name as city_name, " +\
        "main_location, summary, image, eve.status_id, sta.name as status_name, country.id as country_id, city.id  as city_id, " +\
        "eve.profile_id as profile_id " + str_from
    
    str_where = " WHERE (sta.name = 'INITIADED' or sta.name = 'FINALIZED') "  
    
    if criteria_key == 'location':  # por ubicacion
        # buscar el perfil y coger de allí la ciudad y país.
        one_user = get_one_profile(profile_id, db=db)  # Migue me pasa cualquier perfil
        if not one_user:
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_exist"))
        
        if one_user.city_id:
            if criteria_value == 'MY_COUNTRY':
                str_where += " And city.country_id = " + str(one_user.city.country_id)
            elif criteria_value == 'MY_CITY':
                str_where += " And eve.city_id = " + str(one_user.city_id)
                
    elif criteria_key == 'moment':  # por fechas
        # 0: Cualquier fecha, 1: Hoy, 2: Mañana, 3: Este Fin de Semana, 4: Esta semana, 5: próxima Semana, 6: Este mes
        if criteria_value != '0':
            begin_date, end_date = get_dates_from_criteria(criteria_value)
            if begin_date:
                str_where += " And start_date >= '" + begin_date.strftime('%Y-%m-%d') + \
                    "' AND start_date < '" + end_date.strftime('%Y-%m-%d') + "' "
        
    elif criteria_key == 'following':  # los que estoy siguiendo
        str_where += " AND eve.id IN (SELECT element_id FROM events.events_followers foll " +\
            "WHERE foll.element_type = 'EVENT' and foll.profile_id = '" + profile_id + "') "
        
    elif criteria_key == 'participating':  # los que estoy participando
        # participando como jugador o participando como arbitro.
        currentUser = get_current_user(request)
        
        str_where += " AND eve.id IN (Select tourney.event_id from events.domino_boletus_position bpos " +\
            "join events.domino_boletus bol ON bol.id = bpos.boletus_id join events.tourney ON tourney.id = bol.tourney_id " +\
            "where bpos.single_profile_id IN (SELECT pmem.id FROM enterprise.profile_users puse " +\
            "JOIN enterprise.profile_member pmem ON pmem.id = puse.profile_id " +\
            "Where username = '" + currentUser['username'] + "' and profile_type = 'SINGLE_PLAYER')) "
    else:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if str_where == " WHERE (sta.name = 'INITIADED' or sta.name = 'FINALIZED') ": # eso es que no cumplio ninguna condición   
        result.data = [] 
          
    str_count += str_where
    str_query += str_where
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY start_date DESC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db, incluye_tourney=True, api_uri=api_uri, only_iniciaded=True) for item in lst_data]
    return result

def get_dates_from_criteria(criteria_value):
    
    # 0: Cualquier fecha, 1: Hoy, 2: Mañana, 3: Este Fin de Semana, 4: Esta semana, 5: próxima Semana, 6: Este mes
    
    date_now = date.today()
    begin_date, end_date = None, None
    if criteria_value == '1':
        begin_date, end_date = date_now, date_now + timedelta(days=1)
    elif criteria_value == '2':
        begin_date, end_date = date_now + timedelta(days=1), date_now + timedelta(days=2)
    elif criteria_value == '3':
        day_number = date_now.weekday()  #sabado es el dia 5
        amount_day = 5 - day_number # el 5 es sabado
        begin_date, end_date = date_now + timedelta(days=amount_day), date_now + timedelta(days=amount_day+2)
    elif criteria_value == '4':
        day_number = date_now.weekday()
        amount_day = 6 - day_number  # el 6 es domingo
        begin_date, end_date = date_now - timedelta(days=day_number), date_now + timedelta(days=amount_day+1)
    elif criteria_value == '5':
        day_number = date_now.weekday()
        amount_day = 7 - day_number  # el 6 es domingo
        begin_date, end_date = date_now + timedelta(days=amount_day), date_now + timedelta(days=amount_day+7)
    elif criteria_value == '6':
        year = date_now.year + 1 if date_now.month == 12 else date_now.year
        month = 1 if date_now.month == 12 else date_now.month + 1
        begin_date, end_date = date(date_now.year, date_now.month, 1), date(year, month, 1)
    
    return begin_date, end_date

def create_dict_row(item, page, db: Session, incluye_tourney=False, api_uri="", only_iniciaded=False):
    
    image = api_uri + "/api/image/" + str(item['profile_id']) + "/" + item['id'] + "/" + item['image'] if item['image'] else None
    
    new_row = {'id': item['id'], 'name': item['name'], 
               'startDate': item['start_date'], 'endDate': item['close_date'], 
               'country': item['country_id'], 'city': item['city_id'],
               'city_name': item['city_name'], 'campus': item['main_location'], 
               'summary' : item['summary'],
               'photo' : image, 'tourney':[]}
    if page != 0:
        new_row['selected'] = False
    
    if incluye_tourney:
        new_row['tourney'] = get_lst_tourney_by_event_id(item['id'], db=db)
    
    new_row['amount_people'] = get_number_people_at_event(item['id'], "EVENT", db=db) 
        
    return new_row

def get_one(event_id: str, db: Session):  
    return db.query(Event).filter(Event.id == event_id).first()

def get_one_by_name(event_name: str, db: Session):  
    return db.query(Event).filter(Event.name == event_name).first()

def get_one_by_id(event_id: str, db: Session): 
    result = ResultObject()  
    
    api_uri = str(settings.api_uri)
    
    str_query = "Select eve.id, eve.name, start_date, close_date, registration_date, registration_price, city.name as city_name, " +\
        "main_location, summary, image, eve.status_id, sta.name as status_name, country.id as country_id, city.id  as city_id, " +\
        "eve.profile_id as profile_id " +\
        "FROM events.events eve " +\
        "JOIN resources.entities_status sta ON sta.id = eve.status_id " +\
        "JOIN resources.city city ON city.id = eve.city_id " +\
        "JOIN resources.country country ON country.id = city.country_id " +\
        " WHERE eve.id = '" + str(event_id) + "' "  
    lst_data = db.execute(str_query) 
    
    if lst_data: 
        for item in lst_data: 
            result.data = create_dict_row(item, 0, db=db, incluye_tourney=True, api_uri=api_uri)
        if not result.data:
            raise HTTPException(status_code=404, detail="event.not_found")
    else:
        raise HTTPException(status_code=404, detail="event.not_found")
    
    return result

def new(request: Request, profile_id:str, event: EventBase, db: Session, file: File):
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    # si el perfil no es de administrador de eventos, no lo puede crear
    
    db_member_profile = get_one_profile(id=profile_id, db=db)
    if not db_member_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
   
    if db_member_profile.profile_type != 'EVENTADMON':
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.user_not_event_admon"))
    
    one_status = get_one_status_by_name('CREATED', db=db)
    if not one_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    verify_dates(event['start_date'], event['close_date'], locale)
    
    id = str(uuid.uuid4())
    path = create_dir(entity_type="EVENT", user_id=str(db_member_profile.id), entity_id=str(id))
    
    if file:
        ext = get_ext_at_file(file.filename)
        file.filename = str(id) + "." + ext
        
    else:
        file.filename = str(id) + ".jpg"
        
    db_event = Event(id=id, name=event['name'], summary=event['summary'], start_date=event['start_date'], 
                    close_date=event['close_date'], registration_date=event['start_date'], 
                    image=file.filename if file else None, registration_price=float(0.00), 
                    city_id=event['city_id'], main_location=event['main_location'], status_id=one_status.id,
                    created_by=currentUser['username'], updated_by=currentUser['username'], 
                    profile_id=profile_id)
    
    try:
        if file:
            upfile(file=file, path=path)
        else:
            image_domino="public/user-vector.jpg"
            filename = str(id) + ".jpg"
            image_destiny = path + filename
            copy_image(image_domino, image_destiny)
            
        db.add(db_event)
        db.commit()
        result.data = {'id': id}
        return result
       
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "event.error_new_event")               
        raise HTTPException(status_code=403, detail=msg)

def verify_dates(start_date, close_date, locale):
    
    if start_date > close_date:
        raise HTTPException(status_code=404, detail=_(locale, "event.start_date_incorrect"))
    
    return True
 
def delete(request: Request, event_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_status = get_one_status_by_name('CANCELLED', db=db)
    if not one_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    try:
        db_event = db.query(Event).filter(Event.id == event_id).first()
        if db_event:
            db_event.status_id = one_status.id
            db_event.updated_by = currentUser['username']
            db_event.updated_date = datetime.now()
            db.commit()
            
            if db_event.image:
                user_created = get_one_by_username(db_event.created_by, db=db)
                path = "/public/events/" + str(user_created.id) + "/" + str(db_event.id) + "/"
                try:
                    del_image(path=path, name=str(db_event.image))
                except:
                    pass
                try:
                    remove_dir(path=path[:-1])
                except:
                    pass
                
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "event.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "event.imposible_delete"))
    
def update(request: Request, event_id: str, event: EventBase, db: Session, file: File):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
       
    db_event = db.query(Event).filter(Event.id == event_id).first()
    
    # para modificar el rol tiene que ser admon de evento.
    profile_admon_id = get_one_profile_by_user(currentUser['username'], 'EVENTADMON', db=db)
    if not profile_admon_id:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.user_not_event_admon"))
    
    if db_event:
        
        if db_event.status_id == 4:  # FINALIZED
            raise HTTPException(status_code=400, detail=_(locale, "event.event_closed"))
    
        if event['name'] and db_event.name != event['name']:
            db_event.name = event['name']
        
        if event['summary'] and db_event.summary != event['summary']:    
            db_event.summary = event['summary']
        
        if file:
            ext = get_ext_at_file(file.filename)
            
            current_image = db_event.image
            file.filename = str(uuid.uuid4()) + "." + ext if ext else str(uuid.uuid4())
            path = create_dir(entity_type="EVENT", user_id=profile_admon_id, entity_id=str(db_event.id))
            
            path_del = "/public/events/" + str(profile_admon_id) + "/" + str(db_event.id) + "/"
            try:
                del_image(path=path_del, name=str(current_image))
            except:
                pass
            upfile(file=file, path=path)
            db_event.image = file.filename
        
        if event['start_date'] and db_event.start_date != event['start_date']:    
            db_event.start_date = event['start_date']
            
        if event['close_date'] and db_event.close_date != event['close_date']:    
            db_event.close_date = event['close_date']
            
        if event['city_id'] and db_event.city_id != event['city_id']:    
            db_event.city_id = event['city_id']
            
        if event['main_location'] and db_event.main_location != event['main_location']:    
            db_event.main_location = event['main_location']
        
        #desde la interfaz, los que no vengan borrarlos, si vienen nuevos insertarlos, si coinciden modificarlos
        str_tourney_iface = ""
        dict_tourney = {}
        for item in db_event.tourney:
            dict_tourney[item.id] = item
        
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

def get_lst_tourney_by_event_id(event_id: str, db: Session, only_iniciaded=False): 
    
    lst_return = []
    
    str_from = "FROM events.tourney tou " +\
        "JOIN resources.entities_status sta ON sta.id = tou.status_id "
    
    str_query = "Select tou.id, event_id, tou.modality, tou.name, tou.summary, tou.start_date, " +\
        "tou.status_id, sta.name as status_name " + str_from
    
    if only_iniciaded:
        str_query += " WHERE (sta.name = 'INITIADED' or sta.name = 'FINALIZED') and event_id = '" + str(event_id) + "' ORDER BY start_date "  
    else:
        str_query += " WHERE sta.name != 'CANCELLED' and event_id = '" + str(event_id) + "' ORDER BY start_date "  
    lst_data = db.execute(str_query)
    lst_return = [create_dict_row_tourney(item) for item in lst_data]
    
    return lst_return

def get_number_people_at_event(id: str, type_event: str, db: Session): 
    
    str_select = "SELECT eve_r.profile_id, tourney_id, tor.event_id "
    str_from_ref = "FROM events.referees eve_r "
    str_from_play = "FROM events.players eve_r "
    str_inner = "INNER JOIN events.tourney tor ON tor.id = eve_r.tourney_id "
    str_where = "WHERE is_active = True "
    if type_event == 'EVENT':
        str_where += "AND tor.event_id = '" + str(id) + "' "
    elif type_event == 'TOURNEY':
        str_where += "AND tor.tourney_id = '" + str(id) + "' "
    
    str_query = "Select count(*) FROM (" + str_select + str_from_ref + str_inner + str_where
    str_query += " UNION " + str_select + str_from_play + str_inner + str_where
    str_query += " ) as people "
    
    return db.execute(str_query).fetchone()[0]

def create_dict_row_tourney(item):
    
    new_row = {'id': item['id'], 'event_id': item['event_id'], 'name': item['name'], 
               'modality': item['modality'], 'summary' : item['summary'], 'startDate': item['start_date'],
               'status_id': item['status_id'], 'status_name': item['status_name'] 
               }
       
    return new_row

def get_image_event(event_id: str, db: Session): 
    
    db_event = db.query(Event).filter(Event.id == event_id).first()
    
    user_created = get_one_by_username(db_event.created_by, db=db)
    path = "/public/events/" + str(user_created.id) + "/" + str(db_event.id) + "/" + db_event.image
    
    return path

def add_one_followers(request: Request, profile_id: str, event_follower: EventFollowers, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    db_event = db.query(Event).filter(Event.id == event_follower.event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail=_(locale, "event.not_found"))
    
    one_profile = get_one_profile(profile_id, db=db)
    if not one_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    one_followers = get_element_followers_by_criteria(one_profile.id, 'EVENT', db_event.id, db=db)
    if one_followers:
        result.data = one_followers.id
        if not one_followers.is_active:
            update_element_followers(one_followers, True, db=db)
    else:
        result.data = created_element_followers(one_profile.id, currentUser['username'], 'EVENT', db_event.id, db=db)
    
    return result

def remove_one_followers(request: Request, profile_id: str, event_follower: EventFollowers, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
       
    db_event = db.query(Event).filter(Event.id == event_follower.event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail=_(locale, "event.not_found"))
    
    one_profile = get_one_profile(profile_id, db=db)
    if not one_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    one_followers = get_element_followers_by_criteria(one_profile.id, 'EVENT', db_event.id, db=db)
    if one_followers:
        result.data = one_followers.id
        if one_followers.is_active:
            update_element_followers(one_followers, False, db=db)
    else:
        raise HTTPException(status_code=400, detail=_(locale, "events.event_followers_not_exists"))
        
    return result

# para los seguidores de elementos de los eventos
def created_element_followers(profile_id: str, username: str, element_type: str, element_id: str, db: Session):
    
    id=str(uuid.uuid4())
    one_element = EventsFollowers(id=id, profile_id=profile_id, username=username, element_type=element_type,
                                  element_id=element_id, created_by=username, created_date=datetime.today(), is_active=True)
    
    try:
        db.add(one_element)
        db.commit()
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return None
    
    return id

def update_element_followers(one_element, is_active: bool, db: Session):
    
    one_element.is_active = is_active
                
    try:
        db.add(one_element)
        db.commit()
        return True
    except:
        return False

def get_element_followers_by_criteria(profile_id: str, element_type: str, element_id: str, db: Session, is_active=None):
    
    if is_active:
        return db.query(EventsFollowers).filter(EventsFollowers.profile_id == profile_id).\
            filter(EventsFollowers.element_type == element_type).\
            filter(EventsFollowers.element_id == element_id).\
            filter(EventsFollowers.is_active == is_active).first()
    else:
        return db.query(EventsFollowers).filter(EventsFollowers.profile_id == profile_id).\
        filter(EventsFollowers.element_type == element_type).\
        filter(EventsFollowers.element_id == element_id).first()
        
def get_element_followers_by_id(id: str, db: Session):
    return db.query(EventsFollowers).filter(EventsFollowers.id == id).first()
    