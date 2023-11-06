import math
import datetime

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _

from domino.models.notifications.notifications import Notifications
from domino.schemas.notifications.notifications import NotificationsBase
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.utils import get_result_count
            
def get_all(request:Request, profile_id, page: int, per_page: int, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_count = "Select count(*) FROM notifications.notifications WHERE profile_id= '" + profile_id + "' "
    str_query = "Select id, subject, summary, created_date FROM notifications.notifications WHERE profile_id= '" + profile_id + "' "
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
        
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
        
    str_query += " ORDER BY created_date "
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db) for item in lst_data]
            
    return result

def create_dict_row(item, page, db: Session):
    
    new_row = {'id': item['id'], 'subject' : item['subject'], 'summary': item['summary'], 'created_date': item['created_date']}
    if page != 0:
        new_row['selected'] = False
    return new_row

def get_one(id: str, db: Session):  
    return db.query(Notifications).filter(Notifications.id == id).first()

      
def new(request, db: Session, notifications: NotificationsBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_notifications = Notifications(
        subject=notifications.subject, summary=notifications.summary, profile_id=notifications.profile_id, 
        created_by=currentUser['username'], created_date=datetime.datetime.now())
    
    try:
        db.add(db_notifications)
        db.commit()
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "notifications.error_new_post_type")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'name':
                msg = msg + _(locale, "posttype.already_exist")
        
        raise HTTPException(status_code=403, detail=msg)