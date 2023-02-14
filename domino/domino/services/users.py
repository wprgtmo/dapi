# users.py

import math

from fastapi import HTTPException, Request
from domino.models.user import Users
from domino.schemas.user import UserCreate, UserShema, ChagePasswordSchema, UserBase
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from typing import List
from domino.app import _

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
    
    result = ResultObject(page=page, per_page=per_page)
      
    str_where = "WHERE use.is_active=True " 
    str_count = "Select count(*) FROM enterprise.users use "
    str_query = "Select use.id, username, fullname, email, phone, password, use.is_active, pais_id, pa.nombre as pais " \
        "FROM enterprise.users use left join configuracion.pais pa ON pa.id = use.pais_id "

    dict_query = {'username': " AND username ilike '%" + criteria_value + "%'",
                  'fullname': " AND fullname ilike '%" + criteria_value + "%'",
                  'pais': " AND pa.nombre ilike '%" + criteria_value + "%'",
                  'id': " AND id = '" + criteria_value + "' "}
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "users.invalid_param"))
    
    str_where = str_where + dict_query[criteria_key] if criteria_value else str_where  
    str_count += str_where 
    str_query += str_where
    
    result.total = db.execute(str_count).scalar()
    result.total_pages=result.total/result.per_page if (result.total % result.per_page == 0) else math.trunc(result.total / result.per_page) + 1
    
    str_query += " ORDER BY username LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = []
    for item in lst_data:
        result.data.append(
            {'id': item['id'], 'username' : item['username'], 'fullname': item['fullname'],  
            'email': item['email'], 'phone': item['phone'], 'password': item['password'], 
            'pais_id': item['pais_id'], 'pais': item['pais'], 'selected': False})
    
    return result
        
def new(request: Request, db: Session, user: UserCreate):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    pass_check = password_check(user.password, 8, 15)   
    if not pass_check['success']:
        raise HTTPException(status_code=404, detail=_(locale, "users.data_error") + pass_check['message'])             
    
    user.password = pwd_context.hash(user.password)  
    db_user = Users(username=user.username, fullname=user.fullname, pais_id=user.pais_id,  
                    email=user.email, phone=user.phone, password=user.password)
        
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
        
        raise HTTPException(status_code=403, detail=_(locale, "users.new_user_error") + msg) 
        
def get_one(user_id: str, db: Session):  
    return db.query(Users).filter(Users.id == user_id).first()

def get_one_by_id(user_id: str, db: Session): 
    result = ResultObject() 
    result.data = db.query(Users).filter(Users.id == user_id).first()
    return result

def get_one_by_username(username: str, db: Session):  
    return db.query(Users).filter(Users.username == username, Users.is_active == True).first()

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
    db_user.username = user.username
    db_user.fullname = user.fullname
    db_user.pais_id = user.pais_id
    db_user.email = user.email
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
