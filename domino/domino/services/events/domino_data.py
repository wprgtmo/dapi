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
from domino.schemas.events.domino_data import DominoDataCreated

def get_all_data_by_boletus(request:Request, page: int, per_page: int, round_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    lst_data = [{'number': '1', 'pair_one': 10, 'pair_two': 0}, {'number': '2', 'pair_one': 0, 'pair_two': 20},
                {'number': '3', 'pair_one': 50, 'pair_two': 0}, {'number': '4', 'pair_one': 0, 'pair_two': 182}]
                    
    dict_result = {'round_number': '1', 'table_number': '1', 
                   'pair_one' : {'pairs_id': '556666', 'name': 'Juan - Pepe', 'total_point': '60'},
                   'pair_two' : {'pairs_id': '556677', 'name': 'Jorge - Joaquin', 'total_point': '202'},
                   'lst_data': lst_data}
    
    result.data = dict_result
    
    return result

def new_data(request: Request, boletus_id:str, dominodata: DominoDataCreated, db: Session):
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    return result
    
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