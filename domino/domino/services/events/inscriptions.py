import math
from datetime import datetime

from domino.config.config import settings
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _

from domino.models.resources.status import StatusElement
from domino.models.events.inscriptions import Inscriptions

from domino.schemas.events.inscriptions import InscriptionsBase
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.utils import get_result_count
from domino.services.events.tourney import get_one as get_tourney_by_id
from domino.services.enterprise.users import get_one_by_username
from domino.services.resources.status import get_one_by_name as get_status_by_name
from domino.services.resources.country import get_one_by_name as get_country_by_name
from domino.services.enterprise.userprofile import get_type_level

from domino.services.enterprise.auth import get_url_avatar

def get_one(inscriptions_id: str, db: Session):  
    return db.query(Inscriptions).filter(Inscriptions.id == inscriptions_id).first()

def get_all(request:Request, tourney_id:str, page: int, per_page: int, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    str_from = "FROM events.inscriptions ins " +\
        "JOIN resources.entities_status sta ON sta.name = ins.status_name " +\
        "JOIN enterprise.profile_member pm ON pm.id = ins.profile_id " 
                
    str_count = "Select count(*) " + str_from
    str_query = "Select profile_id, pm.name, was_pay, payment_way, import_pay, pm.photo " + str_from
    
    str_where = " WHERE sta.name != 'CANCELLED' AND tourney_id = '" + tourney_id + "' "  
    
    str_search = ''
    if criteria_value:
        str_search = "AND (pm.name ilike '%" + criteria_value + "%' OR pm.payment_way ilike '%" + criteria_value + "%')"
        str_where += str_search
        
    str_count += str_where
    str_query += str_where
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY pm.name DESC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_invitation(item, api_uri=api_uri) for item in lst_data]
    
    return result

def create_dict_row_invitation(item, api_uri=""):
    
    dict_row = {'profile_id': item['profile_id'], 'name': item['name'], 
               'was_pay': item['was_pay'], 'payment_way': item['payment_way'] if item['payment_way'] else '', 
               'import_pay': item['import_pay'] if item['import_pay'] else '0.00', 
               'photo' : get_url_avatar(item['profile_id'], item['photo'], api_uri=api_uri)}
    
    return dict_row

def new(request: Request, profile_id:str, inscriptions: InscriptionsBase, db: Session):
    
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