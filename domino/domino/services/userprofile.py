import math
import uuid

from datetime import datetime

from domino.config.config import settings
from fastapi import HTTPException, Request, File
from unicodedata import name
from domino.functions_jwt import get_current_user
from fastapi import HTTPException
from domino.models.userprofile import ProfileMember, ProfileUsers, SingleProfile
from domino.schemas.userprofile import SingleProfileCreated
from domino.schemas.result_object import ResultObject, ResultData
from domino.services.profiletype import get_one as get_profile_type_by_id, get_one_by_name as get_profile_type_by_name
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.app import _
from domino.services.users import get_one_by_username
from domino.services.utils import upfile, create_dir, del_image, get_ext_at_file, remove_dir, copy_image

from domino.services.auth import get_url_avatar

def new_profile(request: Request, username: str, name:str, profile_type_id: str, email:str, city_id:int, 
                photo:str, receive_notifications: bool, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    profile_type = get_profile_type_by_id(profile_type_id, db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "event.event_closed"))
    
    one_profile = ProfileMember(id=str(uuid.uuid4()), name=name, email=email, profile_type=profile_type, 
                                city_id=city_id, photo=photo, receive_notifications=receive_notifications, 
                                is_active=True, is_ready=True, 
                                created_by=username, updated_by=username)
    
    one_user_member = ProfileUsers(profile_id=one_profile.id, username=username, is_principal=True, created_by=username)
    one_profile.profile_users.append(one_user_member)  
    
    if profile_type.name == "SINGLE_PLAYER":
        one_single_player = SingleProfile(profile_id=one_profile.id, elo=0, ranking='')
        one_profile.profile_single_player.append(one_single_player)
    
    try:
        db.add(one_profile)
        return True
    except (Exception, SQLAlchemyError) as e:
        return False
    
def new_profile_single_player(request: Request, singleprofile: SingleProfileCreated, file: File, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    profile_type = get_profile_type_by_name("SINGLE_PLAYER", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    # si ya tengo perfil no permitir crear otro.
    exist_profile_id = get_one_profile_id(currentUser['username'], "SINGLE_PLAYER", db=db)
    if exist_profile_id:
        raise  HTTPException(status_code=400, detail=_(locale, "userprofile.existprofile"))
    
    id = str(uuid.uuid4())
    
    one_profile = ProfileMember(id=id, name=singleprofile['name'], email=singleprofile['email'], 
                                profile_type=profile_type.name, 
                                city_id=singleprofile['city_id'], photo=file.filename if file else None, 
                                receive_notifications=singleprofile['receive_notifications'], 
                                is_active=True, is_ready=True, 
                                created_by=currentUser['username'], updated_by=currentUser['username'])
    
    one_user_member = ProfileUsers(profile_id=id, username=currentUser['username'], is_principal=True, 
                                   created_by=currentUser['username'])
    one_profile.profile_users.append(one_user_member)  
    
    one_single_player = SingleProfile(profile_id=id, elo=0, ranking=None, updated_by=currentUser['username'])
    one_profile.profile_single_player.append(one_single_player)
    
    path = create_dir(entity_type="USERPROFILE", user_id=str(currentUser['user_id']), entity_id=str(id))
    if file:
        ext = get_ext_at_file(file.filename)
        file.filename = str(id) + "." + ext
        one_profile.photo = file.filename
        upfile(file=file, path=path)
        
    else:
        image_domino="public/profile/user-vector.jpg"
        filename = str(id) + ".jpg"
        image_destiny = "public/profile/" + str(currentUser['user_id']) + "/" + filename
        copy_image(image_domino, image_destiny)
        one_profile.photo = filename
        
    try:   
        db.add(one_profile)
        db.commit()
        result.data = {'id': id}
        return result
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.errorinsert"))

def get_one(id: str, db: Session):  
    return db.query(ProfileMember).filter(ProfileMember.id == id).first()

def get_one_single_profile(id: str, db: Session): 
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "user_id " +\
        "FROM enterprise.profile_member pro join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.id='" + id + "' "
        
    res_profile=db.execute(str_query)
    for item in res_profile:
        photo = get_url_avatar(item.user_id, item.photo, host=host, port=port)
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_id': '', 'profile_type_name': '', 'photo': photo,
                       'city_id': item.city_id, 'receive_notifications': item.receive_notifications}
    
    return result
    
def get_one_profile_id(id: str, db: Session): 
    str_query = "Select pro.id FROM enterprise.profile_member pro join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.id='" + id + "' "
        
    res_profile_id=db.execute(str_query)
    profile_id=res_profile_id[0] if res_profile_id else ""
    return profile_id

def update_one_single_profile(request: Request, id: str, singleprofile: SingleProfileCreated, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_single_profile = get_one(id, db=db)
    if not db_single_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    if singleprofile['name'] and db_single_profile.name != singleprofile['name']:
        db_single_profile.name = singleprofile['name']
        
    if singleprofile['email'] and db_single_profile.email != singleprofile['email']:
        db_single_profile.email = singleprofile['email']
        
    if singleprofile['city_id'] and db_single_profile.city_id != singleprofile['city_id']:
        db_single_profile.city_id = singleprofile['city_id']
        
    db_single_profile.receive_notifications = singleprofile['receive_notifications']
    
    path = create_dir(entity_type="USERPROFILE", user_id=str(currentUser['user_id']), entity_id=db_single_profile.id)    
    if file:
        ext = get_ext_at_file(file.filename)
        current_image = db_single_profile.photo
        file.filename = str(uuid.uuid4()) + "." + ext if ext else str(uuid.uuid4())
        db_single_profile.photo = file.filename
        path_del = "/public/profile/" + str(currentUser['user_id']) + "/" 
        try:
            del_image(path=path_del, name=str(current_image))
        except:
            pass
        upfile(file=file, path=path)
        
    else:
        if not db_single_profile.photo:
            image_domino="public/profile/user-vector.jpg"
            filename = str(currentUser['user_id']) + ".jpg"
            image_destiny = "public/profile/" + str(currentUser['user_id']) + "/" + str(filename)
        
            copy_image(image_domino, image_destiny)
            db_single_profile.photo = filename
            
    try:
        db.add(db_single_profile)
        db.commit()
        db.refresh(db_single_profile)
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))

 
def delete_one_single_profile(request: Request, id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    try:
        db_profile = db.query(ProfileMember).filter(ProfileMember.id == id).first()
        if db_profile:
            db_profile.is_active = False
            db_profile.updated_by = currentUser['username']
            db_profile.updated_date = datetime.now()
            db.commit()
            
            if db_profile.photo:
                user_created = get_one_by_username(currentUser['username'], db=db)
                path = "/public/profile/" + str(user_created.id) + "/" + str(db_profile.id) + "/"
                try:
                    del_image(path=path, name=str(db_profile.photo))
                except:
                    pass
                try:
                    remove_dir(path=path[:-1])
                except:
                    pass
                
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.imposible_delete"))
                                      
def get_user_profile(username: str, profile_type: str, db: Session): 
    str_exist = "Select pro.id FROM enterprise.profile_member pro join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.is_active = True and username='" + username + "' AND pro.profile_type = '" + profile_type + "' "
        
    res_profile_id=db.execute(str_exist).fetchone()
    profile_id=res_profile_id[0] if res_profile_id else ""
    return profile_id

def update_user_profile(profile_id:str, is_active:bool, db: Session):
    str_update = " UPDATE enterprise.profile_member pro SET is_active=is_active " +\
            "WHERE pro.id '" + profile_id + "'; "
            

    