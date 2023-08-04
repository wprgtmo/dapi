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

from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user

from domino.app import _

from domino.config.config import settings
from domino.schemas.enterprise.request import RequestAccepted
from domino.schemas.resources.result_object import ResultObject

from domino.services.enterprise.userprofile import get_one as get_one_profile, get_user_for_single_profile_by_user, \
    get_profile_user_ids, get_count_user_for_status, get_info_owner_profile

from domino.services.enterprise.auth import get_url_avatar

def get_request_to_confirm_at_profile(request:Request, profile_id: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    db_member_profile = get_one_profile(id=profile_id, db=db)
    if not db_member_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    # si el profile no es jugador simple, buscarlo
    single_profile_id = get_user_for_single_profile_by_user(
        currentUser['username'], db=db) if \
            db_member_profile.profile_type != 'SINGLE_PLAYER' else db_member_profile.id
    
    if not single_profile_id:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.sigle_profile_not_exist"))
    
    str_query = "SELECT profile_member.id, profile_member.profile_type, " +\
        "profile_member.name, enterprise.profile_type.description " +\
        "FROM enterprise.profile_users us " +\
        "JOIN enterprise.profile_member ON profile_member.id = us.profile_id " +\
        "JOIN enterprise.profile_type ON profile_type.name = profile_member.profile_type " +\
        "WHERE profile_member.is_active = True AND is_confirmed = False " +\
        "AND us.single_profile_id = '" + single_profile_id + "' "
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, single_profile_id, db=db, host=host, port=port) for item in lst_data]
    
    return result

def create_dict_row(item, single_profile_id, db: Session, host="", port=""):
    # buscar datos del creador de ese perfil
    profile_id, name, photo, elo, ranking = get_info_owner_profile(item['id'], db=db)
    
    return {'profile_id': item['id'], 'name': item['name'], 
            'single_profile_id': single_profile_id,
            'profile_type': item['profile_type'],  
            'profile_description': item['description'],  
            'owner_name': name, 'owner_elo': elo, 'owner_ranking': ranking,
            'photo' : get_url_avatar(profile_id, photo, host=host, port=port)}

#profile id es del que esta aceptando...dentro es el perfil de la pareja..    
def update(request: Request, profile_id:str, requestprofile: RequestAccepted, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
       
    db_user_profile = get_profile_user_ids(profile_id=requestprofile.profile_id, single_profile_id=profile_id, db=db)
    if not db_user_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    db_user_profile.is_confirmed = True if requestprofile.accept else False
    db_user_profile.updated_by = currentUser['username']
    db_user_profile.updated_date = datetime.now()
    
    try:
        db.add(db_user_profile)
        db.commit()
        db.refresh(db_user_profile)
    except:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
    
    # si todos los integrantes están confirmados la pareja o equipo están listos
    db_member_profile = get_one_profile(id=requestprofile.profile_id, db=db)
    if not db_member_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
            
    count_user = get_count_user_for_status(requestprofile.profile_id, False, db=db)
    db_member_profile.is_ready = True if count_user == 0 else False
    db_member_profile.updated_by = currentUser['username']
    db_member_profile.updated_date = datetime.now()
        
    try:
        db.add(db_member_profile)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
            
    