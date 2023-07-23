import math
import uuid

from datetime import datetime
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
import json

from domino.config.config import settings
from domino.schemas.request import RequestAccepted
from domino.schemas.result_object import ResultObject
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.services.users import get_one_by_username
from domino.app import _
from domino.services.userprofile import get_one as get_one_profile, get_single_profile_id_for_profile_by_user, \
    get_profile_user_ids, get_count_user_for_status

from domino.services.auth import get_url_avatar

def get_request_to_confirm_at_profile(request:Request, profile_id: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    db_member_profile = get_one_profile(profile_id=profile_id, db=db)
    if not db_member_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    # si el profile no es jugador simple, buscarlo
    single_profile_id = get_single_profile_id_for_profile_by_user(
        currentUser['username'], profile_id=profile_id, db=db) if \
            db_member_profile.profile_type != 'SINGLE_PLAYER' else db_member_profile.id
    
    str_query = "SELECT profile_member.id, profile_member.photo, profile_member.profile_type, " +\
        "profile_member.name, enterprise.profile_type.description " +\
        "FROM enterprise.profile_users us " +\
        "JOIN enterprise.profile_member ON profile_member.id = us.profile_id " +\
        "JOIN enterprise.profile_type ON profile_type.name = profile_member.profile_type " +\
        "WHERE profile_member.is_active = True AND is_confirmed = False " +\
        "AND us.single_profile_id = '" + single_profile_id + "' "
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, single_profile_id, host=host, port=port) for item in lst_data]
    
    return result

def create_dict_row(item, single_profile_id, host="", port=""):
    return {'profile_id': item['id'], 'name': item['name'], 
            'single_profile_id': single_profile_id,
            'profile_type': item['profile_type'],  
            'profile_description': item['description'],  
            'photo' : get_url_avatar(item['id'], item['photo'], host=host, port=port)}
    
def update(request: Request, profile_id:str, single_profile_id:str, requestprofile: RequestAccepted, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
       
    db_user_profile = get_profile_user_ids(profile_id=profile_id, single_profile_id=single_profile_id, db=db)
    if not db_user_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    # si todos los integrantes están confirmados la pareja o equipo están listos
    
    db_member_profile = get_one_profile(profile_id=profile_id, db=db)
    if not db_member_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
            
    if requestprofile.accept:
        db_user_profile.is_confirmed = True
        count_user = get_count_user_for_status(profile_id, False, db=db)
        if count_user == 0:  # equipo o pareja todos confirmados
            db_member_profile.is_ready = True
            
    else:
        db_user_profile.is_confirmed = False
        db_member_profile.is_ready = False
            
    db_user_profile.updated_by = currentUser['username']
    db_user_profile.updated_date = datetime.now()
    
    db_member_profile.updated_by = currentUser['username']
    db_member_profile.updated_date = datetime.now()
        
    try:
        db.add(db_user_profile)
        db.add(db_member_profile)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "invitation.already_exist"))
            
    