# users.py

import math
import random

from fastapi import HTTPException, Request
from domino.models.user import Users
from domino.schemas.user import UserCreate, UserShema, ChagePasswordSchema, UserBase, UserProfile
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from typing import List
from domino.app import _

from domino.services.country import get_one as country_get_one
from domino.services.city import get_one as city_get_one

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
    
    result = ResultData(page=page, per_page=per_page)
      
    str_where = "WHERE use.is_active=True " 
    str_count = "Select count(*) FROM enterprise.users use "
    str_query = "Select use.id, username, first_name, last_name, email, phone, password, use.is_active, country_id, pa.name as country " \
        "FROM enterprise.users use left join resources.country pa ON pa.id = use.country_id "

    dict_query = {'username': " AND username ilike '%" + criteria_value + "%'",
                  'first_name': " AND first_name ilike '%" + criteria_value + "%'",
                  'last_name': " AND last_name ilike '%" + criteria_value + "%'",
                  'country': " AND pa.name ilike '%" + criteria_value + "%'",
                  'id': " AND id = '" + criteria_value + "' "}
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where  
    str_count += str_where 
    str_query += str_where
    
    if page != 0:
        result = ResultData(page=page, per_page=per_page)  
        
        result.total = db.execute(str_count).scalar()
        result.total_pages=result.total/result.per_page if (result.total % result.per_page == 0) else math.trunc(result.total / result.per_page) + 1
    else:
        result = ResultObject()
    
    str_query += " ORDER BY username "
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        new_row = {'id': item['id'], 'username' : item['username'], 'first_name': item['first_name'], 
                   'last_name': item['last_name'], 'email': item['email'], 'phone': item['phone'], 
                   'password': item['password'], 'country_id': item['country_id'], 'country': item['country']}
        
        if page != 0:
            new_row['selected'] = False
            
        result.data.append(new_row)
    
    return result
        
def new(request: Request, db: Session, user: UserCreate):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    pass_check = password_check(user.password, 8, 15)   
    if not pass_check['success']:
        raise HTTPException(status_code=404, detail=_(locale, "users.data_error") + pass_check['message'])             
    
    one_country = country_get_one(user.country_id, db=db)
    if not one_country:
        raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
    
    user.password = pwd_context.hash(user.password)  
    db_user = Users(username=user.username,  first_name=user.first_name, last_name=user.last_name, country_id=user.country_id,  
                    email=user.email, phone=user.phone, password=user.password, is_active=False)
    
    db_user.security_code = random.randint(10000, 99999)  # codigo de 5 caracteres
        
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

def get_one_by_id(user_id: str, db: Session): 
    result = ResultObject() 
    result.data = db.query(Users).filter(Users.id == user_id).first()
    return result

def get_one_by_username(username: str, db: Session):  
    return db.query(Users).filter(Users.username == username, Users.is_active == True).first()

def get_one_profile(request: Request, user_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail=_(locale, "users.not_found"))
    
    result.data = db_user.dict()
    
    return result

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
    # currentUser = get_current_user(request)
    
    try:
        db_user = db.query(Users).filter(Users.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail=_(locale, "users.not_found"))
        db_user.is_active=False
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "users.imposible_delete"))
    
def update(request: Request, user_id: str, user: UserBase, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()
    # currentUser = get_current_user(request)
       
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

def update_one_profile(request: Request, user_id: str, user: UserProfile, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()
    # currentUser = get_current_user(request)
       
    db_user = db.query(Users).filter(Users.id == user_id).first()
    
    if user.username and user.username != db_user.username:
        one_user = get_one_by_username(user.username, db=db)
        if one_user:
            raise HTTPException(status_code=400, detail=_(locale, "users.already_exist"))
        db_user.username = user.username
    
    if user.country_id and user.country_id != db_user.country_id:
        one_country = country_get_one(user.country_id, db=db)
        if not one_country:
            raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
        db_user.country_id = user.country_id
        
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
        
    if user.photo and user.photo != db_user.photo:
        db_user.photo = user.photo
    
    if user.city_id and user.city_id != db_user.city_id:
        one_city = city_get_one(user.city_id, db=db)
        if not one_city:
            raise HTTPException(status_code=404, detail=_(locale, "city.not_found"))
        if one_city.country_id != user.country_id:
            raise HTTPException(status_code=404, detail=_(locale, "city.country_incorrect"))
        db_user.city_id = user.city_id
        
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "users.already_exist"))
        
def  change_password(request: Request, db: Session, password: ChagePasswordSchema):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()
    # currentUser = get_current_user(request)
    
    # if el user_name viene vacio cojo el usario logueado
    if not password.username:
        currentUser = get_current_user(request)
        username = currentUser['username'] 
    else:
        username = password.username
    
    # verificar que existe ese usuario con ese password
    one_user = get_one_by_username(username=username, db=db)
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
