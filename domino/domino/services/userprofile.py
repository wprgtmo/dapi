import math
import uuid

from datetime import datetime

from domino.config.config import settings
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.userprofile import MemberProfile, MemberUsers
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.app import _

from domino.services.status import get_one_by_name as get_status_by_name

def new_member_profie(username: str, name:str, rolevent_name: str, email:str, city_id:int, photo:str, db: Session): 
    
    one_profile = MemberProfile(id=str(uuid.uuid4()), name=name, email=email, rolevent_name=rolevent_name, city_id=city_id,
                                photo=photo, is_active=True, is_ready=True, created_by=username, updated_by=username)
    one_user_member = MemberUsers(profile_id=one_profile.id, username=username, is_principal=True, created_by=username)
    
    one_profile.users_member.append(one_user_member)  
    
    try:
        db.add(one_profile)
        print('escribi profiel')
        return True
    except (Exception, SQLAlchemyError) as e:
        return False
           
def get_user_profile(username: str, rolevent_name: str, db: Session): 
    str_exist = "Select pro.id FROM enterprise.member_profile pro join enterprise.member_users us ON us.profile_id = pro.id " +\
        "Where username='" + username + "' AND pro.rolevent_name = '" + rolevent_name + "' "
        
    res_profile_id=db.execute(str_exist).fetchone()
    profile_id=res_profile_id[0] if res_profile_id else ""
    return profile_id

def update_user_profile(profile_id:str, is_active:bool, db: Session):
    str_update = " UPDATE enterprise.member_profile pro SET is_active=is_active " +\
            "WHERE pro.id '" + profile_id + "'; "
    