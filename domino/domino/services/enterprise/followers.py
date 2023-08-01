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

from domino.functions_jwt import get_current_user
from domino.app import _

from domino.config.config import settings
from domino.models.enterprise.userprofile import ProfileFollowers

from domino.schemas.enterprise.userprofile import ProfileFollowersBase
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.enterprise.userprofile import get_one as get_one_profile

from domino.services.enterprise.auth import get_url_avatar
from domino.services.resources.utils import get_result_count

def get_follower_suggestions_at_profile(request:Request, profile_id:str, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultData() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    db_member_profile = get_one_profile(id=profile_id, db=db)
    if not db_member_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    #En dependencia del tipo de perfil, sugerir los 10 primeros
    str_from = "FROM enterprise.profile_member " +\
        "WHERE is_active = True and profile_type = '" + db_member_profile.profile_type + "' " +\
        "and city_id = " + str(db_member_profile.city_id) +\
        " AND id NOT IN (Select profile_follow_id FROM enterprise.profile_followers where is_active= True " +\
        "AND profile_id = '" + profile_id + "') AND id != '" + profile_id + "'"
        
    str_count = "SELECT count(id) " + str_from
    str_query = "SELECT id, name, photo, profile_type " + str_from
    
    dict_query = {'name': " AND name ilike '%" + criteria_value + "%'",
                  'profile_type': " AND profile_type = '" + criteria_value + "'"
                  }
    
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY name ASC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
        
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, host=host, port=port) for item in lst_data]
    
    return result

def create_dict_row(item, host="", port=""):
    return {'profile_id': item['id'], 'name': item['name'], 
            'profile_type': item['profile_type'],  
            'photo' : get_url_avatar(item['id'], item['photo'], host=host, port=port)}
    

def get_all_follower_by_profile(profile_id: str, db: Session):  
    return db.query(ProfileFollowers).filter(ProfileFollowers.profile_id == profile_id, ProfileFollowers.is_active == True).all()

def get_all_followers(request:Request, profile_id:str, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultData() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    db_member_profile = get_one_profile(id=profile_id, db=db)
    if not db_member_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    str_from = "FROM enterprise.profile_followers " +\
        "INNER JOIN enterprise.profile_member ON profile_member.id = profile_followers.profile_follow_id " +\
        "WHERE profile_id = '" + profile_id + "' "
    
    str_count = "SELECT count(id) " + str_from
    str_query = "SELECT id, name, photo, profile_type " + str_from
    
    dict_query = {'name': " AND name ilike '%" + criteria_value + "%'",
                  'profile_type': " AND profile_type = '" + criteria_value + "'"
                  }
    
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY name ASC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
        
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, host=host, port=port) for item in lst_data]
    
    return result

def get_one_follower(profile_id: str, profile_follow_id: str, db: Session):  
    return db.query(ProfileFollowers).filter(ProfileFollowers.profile_id == profile_id, ProfileFollowers.profile_follow_id == profile_follow_id).first()

def add_one_followers(request: Request, db: Session, profilefollower: ProfileFollowersBase):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    currentUser = get_current_user(request)
    result = ResultObject()
    
    db_member_profile = get_one_profile(profilefollower.profile_id, db=db)
    if not db_member_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    db_member_profile_foll = get_one_profile(profilefollower.profile_follow_id, db=db)
    if not db_member_profile_foll:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    # verificar que no exista ya como seguidor   
    db_profile_follower = get_one_follower(profilefollower.profile_id, profilefollower.profile_follow_id, db=db)
    if db_profile_follower:
        db_profile_follower.created_date=datetime.now()
        db_profile_follower.is_active = True
    else:
        db_profile_follower = ProfileFollowers(
            profile_id=profilefollower.profile_id, username=db_member_profile.created_by, 
            profile_follow_id=profilefollower.profile_follow_id, username_follow=db_member_profile_foll.created_by, 
            created_by=currentUser['username'], created_date=datetime.now(), is_active=True)
        
    try:
        db.add(db_profile_follower)
        db.commit()
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        msg = _(locale, "users.new_user_error")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "users.already_exist")
        
        raise HTTPException(status_code=403, detail=msg) 
    
def remove_one_followers(request: Request, db: Session, profile_id: str, profile_follower_id: str):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    currentUser = get_current_user(request)
    result = ResultObject()
    
    db_profile_follower = get_one_follower(profile_id, profile_follower_id, db=db)
    if not db_profile_follower:
        raise HTTPException(status_code=404, detail=_(locale, "users.folowers_not_found"))
    
    if db_profile_follower:
        db_profile_follower.created_date=datetime.now()
        db_profile_follower.is_active = False
    
    try:
        db.add(db_profile_follower)
        db.commit()
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "users.new_user_error")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "users.already_exist")
        
        raise HTTPException(status_code=403, detail=msg) 
    
