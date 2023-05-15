# users.py

import math
import random
import uuid
import shutil

from datetime import datetime
from fastapi import HTTPException, Request, UploadFile, File
from domino.models.user import Users, UserFollowers
from domino.schemas.user import UserCreate, UserShema, ChagePasswordSchema, UserBase, UserProfile, UserFollowerBase
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from typing import List
from domino.app import _
from domino.services.utils import get_result_count
from domino.config.config import settings

from domino.services.country import get_one as country_get_one
from domino.services.city import get_one as city_get_one

from domino.services.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir, copy_image

from domino.services.auth import get_url_avatar

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def password_check(passwd, min_len, max_len):
      
    RejectSym =['$', '@', '#', '%', '^']
    AcceptSym = ['!', '*', '.', '+', '-', '_', '?', ';', ':', '&', '=']
    
    RespObj = {"success": True, "message": "Contraseña correcta"}
      
    if len(passwd) < min_len:
        RespObj["success"] = False
        RespObj["message"] = "La contraseña no debe tener menos de " + str(min_len) + " carácteres"
          
    if len(passwd) > max_len:
        RespObj["success"] = False
        RespObj["message"] = "La contraseña no debe exceder los " + str(max_len) + " carácteres"
          
    if not any(char.isdigit() for char in passwd):
        RespObj["success"] = False
        RespObj["message"] = "La contraseña debe contar con al menos un Número"
          
    if not any(char.isupper() for char in passwd):
        RespObj["success"] = False
        RespObj["message"] = "La contraseña debe contar con al menos una Mayúscula"
          
    if not any(char.islower() for char in passwd):
        RespObj["success"] = False
        RespObj["message"] = "La contraseña debe contar con al menos una Minúscula"

    if not any(char in AcceptSym for char in passwd):
        RespObj["success"] = False
        RespObj["message"] = "La contraseña debe contener al menos un carácter especial"
        
    if any(char in RejectSym for char in passwd):
        RespObj["success"] = False
        RespObj["message"] = "La contraseña contiene carácteres no permitidos"

    return RespObj

def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    host=str(settings.server_uri)
    port=str(int(settings.server_port))
    
    str_where = "WHERE use.is_active=True " 
    str_count = "Select count(*) FROM enterprise.users use "
    str_query = "Select use.id, username, first_name, last_name, email, phone, password, use.is_active, country_id, " \
        "pa.name as country, use.photo, use.receive_notifications " \
        "FROM enterprise.users use left join resources.country pa ON pa.id = use.country_id "

    dict_query = {'username': " AND username ilike '%" + criteria_value + "%'",
                  'first_name': " AND first_name ilike '%" + criteria_value + "%'",
                  'last_name': " AND last_name ilike '%" + criteria_value + "%'",
                  'country': " AND pa.name ilike '%" + criteria_value + "%'",
                  'id': " AND id = '" + criteria_value + "' "}
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where  
    str_count += str_where 
    str_query += str_where
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY username "
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, host=host, port=port) for item in lst_data]
    
    return result

def create_dict_row(item, page, host='', port=''):
    
    new_row = {'id': item['id'], 'username' : item['username'], 'first_name': item['first_name'], 
               'last_name': item['last_name'], 'email': item['email'], 'phone': item['phone'], 
               'country_id': item['country_id'], 'country': item['country'], 
               'receive_notifications': item['receive_notifications'],
               'photo': get_url_avatar(item['id'], item['photo'], host=host, port=port)}
    if page != 0:
        new_row['selected'] = False
    return new_row
        
def new(request: Request, db: Session, user: UserCreate, avatar: File):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    pass_check = password_check(user.password, 8, 15)   
    if not pass_check['success']:
        raise HTTPException(status_code=404, detail=_(locale, "users.data_error") + pass_check['message'])             
    
    one_country = country_get_one(user.country_id, db=db)
    if not one_country:
        raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
    
    id = str(uuid.uuid4())
    user.password = pwd_context.hash(user.password)  
    db_user = Users(id=id, username=user.username,  first_name=user.first_name, last_name=user.last_name, 
                    country_id=user.country_id, email=user.email, phone=user.phone, password=user.password, 
                    is_active=True, receive_notifications=user.receive_notifications if user.receive_notifications else False)
    
    db_user.security_code = random.randint(10000, 99999)  # codigo de 5 caracteres
    
    path = create_dir(entity_type="USER", user_id=str(id), entity_id=None)
    
    if avatar:
        ext = get_ext_at_file(avatar.filename)
        avatar.filename = str(id) + "." + ext
        db_user.photo = avatar.filename
        upfile(file=avatar, path=path)
    
    else:
        image_domino="public/profile/user-vector.jpg"
        filename = str(id) + ".jpg"
        image_destiny = "public/profile/" + str(db_user.id) + "/" + filename

        copy_image(image_domino, image_destiny)
        db_user.photo = filename
                
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "users.new_user_error")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "users.already_exist")
        
        raise HTTPException(status_code=403, detail=msg) 
        
def get_one(user_id: str, db: Session):  
    return db.query(Users).filter(Users.id == user_id).first()

def get_one_by_id(request: Request, user_id: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    one_user = db.query(Users).filter(Users.id == user_id).first()
    if not one_user:
        raise
    
    one_country = country_get_one(one_user.country_id, db=db)
    if not one_country:
        raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
    
    result.data = {'id': one_user.id, 'username' : one_user.username, 
                   'first_name': one_user.first_name, 
                   'last_name': one_user.last_name if one_user.last_name else '', 
                   'email': one_user.email if one_user.email else '', 
                   'phone': one_user.phone if one_user.phone else '', 
                   'country_id': one_country.id if one_country else '', 
                   'country': one_country.name if one_country else '', 
                   'job': one_user.job if one_user.job else '',
                   'sex': one_user.sex if one_user.sex else '', 
                   'birthdate': one_user.birthdate if one_user.birthdate else '', 
                   'alias': one_user.alias if one_user.alias else '',
                   'city_id': one_user.city_id if one_user.city_id else '',
                   'receive_notifications': one_user.receive_notifications if one_user.receive_notifications else False,  
                   'photo': get_url_avatar(one_user.id, one_user.photo, host=host, port=port)} 
    
    return result

def get_one_by_username(username: str, db: Session):  
    return db.query(Users).filter(Users.username == username, Users.is_active == True).first()

def get_one_follower(username: str, user_follower: str, db: Session):  
    return db.query(UserFollowers).filter(UserFollowers.username == username, UserFollowers.user_follow == user_follower).first()

def get_all_follower_by_user(username: str, db: Session):  
    return db.query(UserFollowers).filter(UserFollowers.username == username, UserFollowers.is_active == True).all()

def get_one_profile(request: Request, user_id: str, db: Session):
    return get_one_by_id(request=request, user_id=user_id, db=db)

def check_security_code(request: Request, username: str, security_code: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()
    
    try:
        db_user = db.query(Users).filter(Users.username == username).first()
        if not db_user:
            raise HTTPException(status_code=404, detail=_(locale, "users.not_found"))
        
        if security_code == db_user.security_code:
            result.success = True
            db_user.is_active = True
            db.commit()
        else:
            result.success = False
            result.detail = _(locale, "users.incorrect_code")
        
        return result

    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "users.imposible_verify"))

def delete(request: Request, user_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()
    
    try:
        db_user = db.query(Users).filter(Users.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail=_(locale, "users.not_found"))
        
        #borrar la foto y la carpeta del usuario
        path_del = "/public/profile/" + str(db_user.id) + "/" 
        try:
            del_image(path=path_del, name=str(db_user.photo))
            # borrar directorio del usuario
            remove_dir(path_del)
        except:
            pass
        
        db_user.photo=None
        db_user.is_active=False
        del_image
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "users.imposible_delete"))
    
def update(request: Request, user_id: str, user: UserBase, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()
       
    db_user = db.query(Users).filter(Users.id == user_id).first()
    
    if user.username != db_user.username:
        one_user = get_one_by_username(user.username, db=db)
        if one_user:
            raise HTTPException(status_code=400, detail=_(locale, "users.already_exist"))
        db_user.username = user.username
    
    if user.country_id != db_user.country_id:
        one_country = country_get_one(user.country_id, db=db)
        if not one_country:
            raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
        db_user.country_id = user.country_id
        
    if user.first_name != db_user.first_name:
        db_user.first_name = user.first_name
        
    if user.last_name != db_user.last_name:
        db_user.last_name = user.last_name
        
    if user.email != db_user.email:
        db_user.email = user.email
        
    if user.phone != db_user.phone:
        db_user.phone = user.phone
        
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "users.already_exist"))

def update_one_profile(request: Request, user_id: str, user: UserProfile, db: Session, avatar: File):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()
       
    db_user = db.query(Users).filter(Users.id == user_id).first()
    
    if user.first_name and user.first_name != db_user.first_name:
        db_user.first_name = user.first_name
        
    if user.last_name and user.last_name != db_user.last_name:
        db_user.last_name = user.last_name
        
    if user.email and user.email != db_user.email:
        db_user.email = user.email
        
    if user.phone and user.phone != db_user.phone:
        db_user.phone = user.phone
        
    if user.sex and user.sex != db_user.sex:
        db_user.sex = user.sex
        
    if user.birthdate and user.birthdate != db_user.birthdate:
        db_user.birthdate = user.birthdate
        
    if user.alias and user.alias != db_user.alias:
        db_user.alias = user.alias
        
    if user.job and user.job != db_user.job:
        db_user.job = user.job
        
    if user.city_id and user.city_id != db_user.city_id:
        one_city = city_get_one(user.city_id, db=db)
        if not one_city:
            raise HTTPException(status_code=404, detail=_(locale, "city.not_found"))
        db_user.city_id = one_city.id
        
    if user.receive_notifications and user.receive_notifications != db_user.receive_notifications:
        db_user.receive_notifications = user.receive_notifications
    
    path = create_dir(entity_type="USER", user_id=str(db_user.id), entity_id=None)    
    if avatar:
        ext = get_ext_at_file(avatar.filename)
        current_image = db_user.photo
        avatar.filename = str(uuid.uuid4()) + "." + ext if ext else str(uuid.uuid4())
        db_user.photo = avatar.filename
        path_del = "/public/profile/" + str(db_user.id) + "/" 
        try:
            del_image(path=path_del, name=str(current_image))
        except:
            pass
        upfile(file=avatar, path=path)
        
    else:
        if not db_user.photo:
            image_domino="public/profile/user-vector.jpg"
            filename = str(db_user.id) + ".jpg"
            image_destiny = "public/profile/" + str(db_user.id) + "/" + str(filename)
        
            copy_image(image_domino, image_destiny)
            db_user.photo = filename
        
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        filename = avatar.filename if avatar else db_user.photo
        result.data = get_url_avatar(db_user.id, filename)
            
        return result
    except (Exception, SQLAlchemyError) as e:
        if e and e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "users.already_exist"))
        
def change_password(request: Request, db: Session, password: ChagePasswordSchema):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()
    
    # if el id viene vacio cojo el usario logueado
    if not password.id:
        currentUser = get_current_user(request)
        one_user = get_one_by_username(username=currentUser['username'], db=db)
    else:
        one_user = get_one(user_id=password.id, db=db)
        
    if not one_user:
        raise HTTPException(status_code=404, detail=_(locale, "users.not_found"))
    
    if pwd_context.verify(password.current_password, one_user.password):
        
        # verificar que las contrasenas nuevas son iguales
        if str(password.new_password) != str(password.renew_password):
            raise HTTPException(status_code=404, detail=_(locale, "users.check_password"))
        
        #verificando que tenga la estructura correcta
        pass_check = password_check(password.new_password, 8, 15)   
        if not pass_check['success']:
            raise HTTPException(status_code=404, detail=_(locale, "users.new_password_incorrect") + pass_check['message']) 
        
        #cambiando el paswword al usuario
        one_user.password = pwd_context.hash(password.new_password)
        
        try:
            db.add(one_user)
            db.commit()
            db.refresh(one_user)
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail=_(locale, "users.change_password_error"))
        
    else:
        raise HTTPException(status_code=405, detail=_(locale, "users.wrong_password"))

def add_one_followers(request: Request, db: Session, userfollower: UserFollowerBase):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    currentUser = get_current_user(request)
    result = ResultObject()
    
    one_user = get_one_by_username(username=currentUser['username'], db=db)
        
    if not one_user:
        raise HTTPException(status_code=404, detail=_(locale, "users.not_found"))
    
    user_followers = get_one_by_username(username=userfollower.user_follow, db=db)
    if not user_followers:
        raise HTTPException(status_code=404, detail=_(locale, "users.not_found"))
    
    # verificar si no existe y ya esta desactivado
    db_user_follower = get_one_follower(one_user.username, userfollower.user_follow, db=db)
    if db_user_follower:
        if db_user_follower.is_active == False:
            db_user_follower.created_date=datetime.datetime.now()
            db_user_follower.is_active = True
    else:
        db_user_follower = UserFollowers(username=one_user.username, user_follow=userfollower.user_follow, 
                                         created_date=datetime.now(), is_active=True)
        
    try:
        db.add(db_user_follower)
        db.commit()
        db.refresh(db_user_follower)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "users.new_user_error")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "users.already_exist")
        
        raise HTTPException(status_code=403, detail=msg) 
    
def remove_one_followers(request: Request, db: Session, user_follower: str):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    currentUser = get_current_user(request)
    result = ResultObject()
    
    db_user_follower = get_one_follower(currentUser['username'], user_follower, db=db)
    if not db_user_follower:
        raise HTTPException(status_code=404, detail=_(locale, "users.folowers_not_found"))
    
    db_user_follower.created_date=datetime.now()
    db_user_follower.is_active = False
        
    try:
        db.add(db_user_follower)
        db.commit()
        db.refresh(db_user_follower)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "users.new_user_error")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "users.already_exist")
        
        raise HTTPException(status_code=403, detail=msg) 
    
    
def get_all_followers(request: Request, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    currentUser = get_current_user(request)
    result = ResultObject()
    
    str_query = "Select us.username, us.first_name || ' ' || us.last_name as full_name, us.photo " +\
        "FROM enterprise.user_followers usf JOIN enterprise.users us ON usf.user_follow = us.username " +\
        "WHERE usf.is_active = True and usf.username = '" + currentUser['username'] + "' ORDER BY created_date DESC "
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_follower(item) for item in lst_data]
    
    return result

def get_all_not_followers(request: Request, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    currentUser = get_current_user(request)
    result = ResultObject()
    
    str_query = "Select us.username, us.first_name || ' ' || us.last_name as full_name, us.photo " +\
        "FROM enterprise.users us WHERE us.is_active = TRUE " +\
        "AND username != '" + currentUser['username'] + "' AND username != 'domino' " +\
        "AND us.username NOT IN (Select user_follow FROM enterprise.user_followers usf WHERE username = '" + currentUser['username'] + "') " +\
        "LIMIT 5 "

    lst_data = db.execute(str_query)
    result.data = [create_dict_row_follower(item) for item in lst_data]
    
    return result

def create_dict_row_follower(item):
    
    return {'username' : item['username'], 'full_name': item['full_name'], 'photo': item['photo'] if item['photo'] else ""}