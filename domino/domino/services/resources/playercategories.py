import math

from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _

from domino.models.resources.eventscategories import EventLevels, EventScopes, PlayerCategories
from domino.schemas.resources.playercategories import EventLevelsBase, EventScopesBase, PlayerCategoriesBase
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.utils import get_result_count

def get_one_event_level(id: int, db: Session):  
    return db.query(EventLevels).filter(EventLevels.id == id).first()

def get_one_event_level_by_name(level: str, db: Session):  
    return db.query(EventLevels).filter(EventLevels.level == level).first()

def get_one_event_scope(id: int, db: Session):  
    return db.query(EventScopes).filter(EventScopes.id == id).first()

def get_one_event_scope_by_name(scope: str, db: Session):  
    return db.query(EventScopes).filter(EventScopes.scope == scope).first()

def get_one_player_category_by_name(category_name: str, db: Session):  
    return db.query(PlayerCategories).filter(PlayerCategories.name == category_name).first()

def get_all_event_level(request:Request, db: Session):  
    result = ResultObject() 
    result.data = db.query(EventLevels).all()
    return result

def get_all_event_scope(request:Request, db: Session):  
    result = ResultObject() 
    result.data = db.query(EventScopes).all()
    return result
      
def new_event_level(request, db: Session, eventslevels: EventLevelsBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    db_level = get_one_event_level_by_name(eventslevels.level, db=db)
    if db_level:
        raise HTTPException(status_code=404, detail=_(locale, "status.exist_name"))
        
    db_level = EventLevels(level=eventslevels.level, description=eventslevels.description, value=eventslevels.value)
    
    try:
        db.add(db_level)
        db.commit()
        db.refresh(db_level)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "status.error_new_status")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "status.already_exist")
        
        raise HTTPException(status_code=403, detail=msg)
    
def new_event_scope(request, db: Session, eventscopes: EventScopesBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    db_scope = get_one_event_scope_by_name(eventscopes.scope, db=db)
    if db_scope:
        raise HTTPException(status_code=404, detail=_(locale, "status.exist_name"))
        
    db_scope = EventScopes(scope=eventscopes.scope, description=eventscopes.description, value=eventscopes.value)
    
    try:
        db.add(db_scope)
        db.commit()
        db.refresh(db_scope)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "status.error_new_status")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "status.already_exist")
        
        raise HTTPException(status_code=403, detail=msg)
    
def new_category_by_elo(request, db: Session, playercategory: PlayerCategoriesBase):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    db_category = get_one_player_category_by_name(playercategory.name, db=db)
    if db_category:
        raise HTTPException(status_code=404, detail=_(locale, "status.exist_name"))
        
    db_category = PlayerCategories(name=playercategory.name, value_k=playercategory.value_k, begin_elo=playercategory.begin_elo,
                                   end_elo=playercategory.end_elo, width=playercategory.width, scope=playercategory.scope)
    
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "status.error_new_status")
        if e.code == 'gkpj':
            field_name = str(e.__dict__['orig']).split('"')[1].split('_')[1]
            if field_name == 'username':
                msg = msg + _(locale, "status.already_exist")
        
        raise HTTPException(status_code=403, detail=msg)
 
