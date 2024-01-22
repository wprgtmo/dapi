# users.py

import math
import random
import uuid
import shutil
import json

from datetime import datetime
from fastapi import HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from typing import List
from domino.app import _
from domino.config.config import settings

from domino.models.enterprise.user import Users, UserFollowers
from domino.models.enterprise.userprofile import ProfileMember

from domino.schemas.enterprise.user import UserCreate, UserShema, ChagePasswordSchema, UserBase, UserFollowerBase
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.country import get_one as country_get_one
from domino.services.resources.city import get_one as city_get_one
from domino.services.enterprise.profiletype import get_one as get_profile_type_by_id, get_one_by_name as get_profile_type_by_name

from domino.services.resources.utils import get_result_count
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir, copy_image

from domino.services.enterprise.auth import get_url_avatar
from domino.services.enterprise.comunprofile import new_profile_default_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def password_check(passwd, min_len, max_len, level):
    RespObj = {"success": True, "message": "Contraseña correcta"}

    if level > 0:
      
        RejectSym =['$', '@', '#', '%', '^']
        AcceptSym = ['!', '*', '.', '+', '-', '_', '?', ';', ':', '&', '=']

        if level == 1:
            if len(passwd) < min_len:
                RespObj["success"] = False
                RespObj["message"] = "La contraseña no debe tener menos de " + str(min_len) + " carácteres"
                
            if len(passwd) > max_len:
                RespObj["success"] = False
                RespObj["message"] = "La contraseña no debe exceder los " + str(max_len) + " carácteres"

        if level == 2:
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


        if level == 3:
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
    
    api_uri = str(settings.api_uri)
    
    str_where = "WHERE use.is_active=True " 
    str_count = "Select count(*) FROM enterprise.users use "
    str_query = "Select use.id, username, first_name, last_name, pro.email, phone, password, use.is_active, country_id, " \
        "pa.name as country, pro.photo, pro.receive_notifications " \
        "FROM enterprise.users use " + \
        "inner join enterprise.profile_member pro ON pro.id = use.id " +\
        "left join resources.country pa ON pa.id = use.country_id "

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
    result.data = [create_dict_row(item, page, api_uri=api_uri) for item in lst_data]
    
    return result

def create_dict_row(item, page, api_uri=''):
    
    new_row = {'id': item['id'], 'username' : item['username'], 'first_name': item['first_name'], 
               'last_name': item['last_name'], 'email': item['email'], 'phone': item['phone'], 
               'country_id': item['country_id'], 'country': item['country'], 
               'receive_notifications': item['receive_notifications'],
               'photo': get_url_avatar(item['id'], item['photo'], api_uri=api_uri)}
    if page != 0:
        new_row['selected'] = False
    return new_row
 
#crear un usuario siempre crea el perfil de ususraio asociado...        
def new(request: Request, db: Session, user: UserCreate):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    #verificar que el nombre de usuario no existe en Base de Datos
    str_user = "SELECT count(username) FROM enterprise.users where username = '" + user.username + "' "
    amount_user = db.execute(str_user).fetchone()[0]
    if amount_user > 0:
        raise HTTPException(status_code=404, detail=_(locale, "users.already_exist"))  
    
    
    pass_check = password_check(user.password, settings.pwd_length_min, settings.pwd_length_max, settings.pwd_level)   
    if not pass_check['success']:
        raise HTTPException(status_code=404, detail=_(locale, "users.data_error") + pass_check['message'])             

    
    one_country = country_get_one(user.country_id, db=db)
    if not one_country:
        raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
    
    id = str(uuid.uuid4())
    user.password = pwd_context.hash(user.password)  
    db_user = Users(id=id, username=user.username,  first_name=user.first_name, last_name=user.last_name, 
                    country_id=user.country_id, email=user.email, phone=user.phone, password=user.password, 
                    is_active=True)
    
    db_user.security_code = random.randint(10000, 99999)  # codigo de 5 caracteres
    
    profile_type = get_profile_type_by_name("USER", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    full_name = user.first_name + ' ' + user.last_name if user.last_name else user.first_name if user.first_name else ''
    profile_id = id  # voy a ahecr coincidir el id de usuario con el del perfil de usuario, tema fotos                     
    one_profile_user = new_profile_default_user(profile_type, profile_id, id, user.username, full_name, user.email, None,
                                                False, user.username, user.username, None, None, None, None, None)
                               
    try:
        db.add(db_user)
        db.add(one_profile_user)
        db.commit()
        db.refresh(db_user)
        result.data = {'id': id}
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "users.new_user_error")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "users.already_exist")
        
        raise HTTPException(status_code=403, detail=msg) 
    
def new_from_register(email: str, username: str, first_name:str, last_name:str, alias:str, phone:str, city_id: int, 
                      created_by:str, file:File, db: Session, locale):  
    
    #verificar que el nombre de usuario no existe en Base de Datos, ni el email
    str_user = "SELECT count(username) FROM enterprise.users where username = '" + username + "' "
    amount_user = db.execute(str_user).fetchone()[0]
    if amount_user > 0:
        raise HTTPException(status_code=404, detail=_(locale, "users.username_exist")) 
    
    str_user = "SELECT count(username) FROM enterprise.users where email = '" + email + "' "
    amount_user = db.execute(str_user).fetchone()[0]
    if amount_user > 0:
        raise HTTPException(status_code=404, detail=_(locale, "users.email_exist"))  
    
    one_city = city_get_one(city_id=city_id, db=db)
    if not one_city:
        raise HTTPException(status_code=404, detail=_(locale, "city.not_found"))
    
    id = str(uuid.uuid4())
    user_password = pwd_context.hash('Dom.1234*')  
    db_user = Users(id=id, username=username,  first_name=first_name, last_name=last_name, country_id=one_city.country.id, 
                    email=email, phone=phone, password=user_password, is_active=True)
    
    db_user.security_code = random.randint(10000, 99999)  # codigo de 5 caracteres
    
    profile_type = get_profile_type_by_name("USER", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    full_name = first_name + ' ' + last_name if last_name else first_name if first_name else ''
    profile_id = id  # voy a hacer coincidir el id de usuario con el del perfil de usuario, tema fotos  
    one_profile_user = new_profile_default_user(profile_type, profile_id, id, username, full_name, email, city_id,
                                                True, created_by, created_by, None, None, alias, None, file=file)
                               
    try:
        db.add(db_user)
        db.add(one_profile_user)
        db.commit()
        return True
    except (Exception, SQLAlchemyError, IntegrityError) as e:
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
    
    api_uri = str(settings.api_uri)
    
    str_query = "Select use.id user_id, username, first_name, last_name, pro.email, phone, password, use.is_active, use.country_id, " \
        "pa.name as country_name, pro.photo, pro.receive_notifications, def.job, def.sex, def.birthdate, def.alias, " \
        "city.id as city_id, city.name as city_name " +\
        "FROM enterprise.users use " + \
        "inner join enterprise.profile_member pro ON pro.id = use.id " +\
        "inner join enterprise.profile_default_user def ON def.profile_id = pro.id " +\
        "left join resources.country pa ON pa.id = use.country_id " +\
        "left join resources.city city ON city.id = pro.city_id "
    
    lst_data = db.execute(str_query)
    if not lst_data:
        raise HTTPException(status_code=404, detail=_(locale, "auth.not_found"))
    
    
    user_id, username, first_name, last_name, photo = '', '', '', '', ''
    email, job, sex, birthdate, alias = '', '', '', '', ''
    is_active, receive_notifications = False, False
    country_id, country_name, city_id, city_name = '', '', '', ''
    for item in lst_data:
        user_id, username = item.user_id, item.username
        first_name, last_name, birthdate = item.first_name, item.last_name, item.birthdate
        email, phone, job, sex = item.email, item.phone, item.job, item.sex
        photo, alias = item.photo, item.alias
        is_active = item.is_active
        country_id, country_name = item.country_id, item.country_name
        city_id, city_name = item.city_id, item.city_name
        
    if is_active is False:
        raise HTTPException(status_code=404, detail=_(locale, "auth.not_registered"))
    
    result.data = {'id': user_id, 'username': username, 
                   'first_name': first_name, 'last_name': last_name if last_name else '', 
                   'email': email if email else '', 'phone': phone if phone else '', 
                   'country_id': country_id if country_id else '', 'country': country_name if country_name else '', 
                   'job': job if job else '', 'sex': sex if sex else '', 'birthdate': birthdate if birthdate else '', 
                   'alias': alias if alias else '',
                   'city_id': city_id if city_id else '', 'city_name': city_name if city_name else '',
                   'receive_notifications': receive_notifications,  
                   'photo': get_url_avatar(user_id, photo, api_uri=api_uri)} 
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
        
        # desactivar el perfil del usuario
        db_profile = db.query(ProfileMember).filter(ProfileMember.id == user_id).first()
        
        #borrar la foto y la carpeta del usuario
        path_del = "/public/profile/" + str(db_user.id) + "/" 
        try:
            del_image(path=path_del, name=str(db_user.photo))
            # borrar directorio del usuario
            remove_dir(path_del)
        except:
            pass
        
        db_user.photo = None
        db_user.is_active = False
        
        if db_profile:
            db_profile.is_active = False
            
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
