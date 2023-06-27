import math
from datetime import datetime

from domino.config.config import settings
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from domino.models.invitations import Invitations
from domino.schemas.invitations import InvitationBase, InvitationAccepted
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _
from domino.services.utils import get_result_count
from domino.services.tourney import get_one as get_tourney_by_id
from domino.services.users import get_one_by_username
from domino.services.status import get_one_by_name as get_status_by_name

def get_one_by_id(invitation_id: str, db: Session):  
    return db.query(Invitations).filter(Invitations.id == invitation_id).first()
           
def get_all_invitations_by_tourney(request, tourney_id: str, status_name:str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    user_id=currentUser['user_id']
    
    host=str(settings.server_uri)
    port=str(int(settings.server_port))
    
    status_name = 'ALL' if not status_name else status_name
                                           
    str_query = "SELECT invitations.id, tourney.name as tourney_name, tourney.modality, tourney.start_date, " + \
        "events.name as event_name, events.close_date, events.main_location, city.name as city_name, " + \
        "country.name country_name, eve.description as rolevent_name, events.id as event_id, events.image " +\
        "FROM events.invitations " + \
        "inner join enterprise.profile_member pro ON pro.id = invitations.profile_id " + \
        "inner join enterprise.profile_users use ON use.profile_id = pro.id " +\
        "inner join events.tourney ON tourney.id = invitations.tourney_id " + \
        "inner join events.events ON events.id = tourney.event_id " + \
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "left join resources.city ON city.id = events.city_id " +\
        "left join resources.country ON country.id = city.country_id " +\
        "WHERE invitations.tourney_id = '" + tourney_id + "' "

    if status_name != 'ALL':
        str_query += " AND invitations.status_name = '" + status_name + "' "
        
    str_query += "ORDER BY tourney.start_date ASC "
        
    lst_inv = db.execute(str_query)
    result.data = [create_dict_row_invitation(item, user_id, host=host, port=port) for item in lst_inv]
    
    return result

def get_all_invitations_by_user(request, status_name:str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    user_id=currentUser['user_id']
    
    host=str(settings.server_uri)
    port=str(int(settings.server_port))
                                            
    str_query = "SELECT invitations.id, tourney.name as tourney_name, tourney.modality, tourney.start_date, " + \
        "events.name as event_name, events.close_date, events.main_location, city.name as city_name, " + \
        "country.name country_name, eve.description as rolevent_name, events.id as event_id, " +\
        "events.image " +\
        "FROM events.invitations " + \
        "inner join enterprise.profile_member pro ON pro.id = invitations.profile_id " + \
        "inner join enterprise.profile_users use ON use.profile_id = pro.id " +\
        "inner join events.tourney ON tourney.id = invitations.tourney_id " + \
        "inner join events.events ON events.id = tourney.event_id " + \
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "left join resources.city ON city.id = events.city_id " +\
        "left join resources.country ON country.id = city.country_id " +\
        "WHERE use.username = '" + currentUser['username'] + "' "

    if status_name != 'ALL':
        str_query += " AND invitations.status_name = '" + status_name + "' "
        
    str_query += "ORDER BY tourney.start_date ASC "
        
    lst_inv = db.execute(str_query)
    result.data = [create_dict_row_invitation(item, user_id, host=host, port=port) for item in lst_inv]
    
    return result
 
def create_dict_row_invitation(item, user_id, host="", port=""):
    
    image = "http://" + host + ":" + port + "/api/image/" + str(user_id) + "/" + item['event_id'] + "/" + item['image']
    
    new_row = {'id': item['id'], 'event_name': item['event_name'], 
               'rolevent_name': item['rolevent_name'],
               'country': item['country_name'], 'city_name': item['city_name'],
               'campus': item['main_location'], 
               'tourney_name': item['tourney_name'], 
               'modality': item['modality'], 
               'startDate': item['start_date'], 'endDate': item['close_date'], 
               'photo' : image}
    
    return new_row
           
def generate_all_user(request, db: Session, tourney_id: str):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_tourney = get_tourney_by_id(tourney_id=tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_exist"))
    
    db_status = get_status_by_name('SEND', db=db)
    if not db_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_exist"))
        
    str_users = "SELECT profile_member.id profile_id, eve.name as rolevent_name  " + \
        "FROM enterprise.profile_member " +\
        "inner join enterprise.profile_users ON profile_users.profile_id = profile_member.id " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "where profile_member.is_active=True and eve.name IN ('SINGLE_PLAYER', 'PAIR_PLAYER', 'TEAM_PLAYER', 'REFEREE') " +\
        "and enterprise.profile_member.modality='" + db_tourney.modality + "' " +\
        "and profile_member.id +\
        "NOT IN (Select profile_id FROM events.invitations where tourney_id = '" + tourney_id + "') "

    lst_data = db.execute(str_users)
    
    try:
        for item in lst_data:
            one_invitation = Invitations(tourney_id=db_tourney.id, profile_id=item.profile_id, 
                                         rolevent_name=item.rolevent_name, modality=db_tourney.modality,
                                         status_name=db_status.name, created_by=currentUser['username'], 
                                         updated_by=currentUser['username'])
            db.add(one_invitation)
            db.commit()
        
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        print(e.__dict__)
        msg = _(locale, "invitation.error_generate_new")
        if e.code == 'gkpj':
            msg = msg + _(locale, "invitation.already_exist")
        
        raise HTTPException(status_code=403, detail=msg)
    
def update(request: Request, invitation_id: str, invitation: InvitationAccepted, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
       
    db_invitation = get_one_by_id(invitation_id, db=db)
    if not db_invitation:
        raise HTTPException(status_code=400, detail=_(locale, "invitation.not_exist"))
    
    if db_invitation.status_name == 'SEND':
        status_name = 'ACCEPTED' if invitation.accept else 'REJECTED'
    else:
        status_name = db_invitation.status_name if invitation.accept else 'SEND'
            
    db_status = get_status_by_name(status_name, db=db)
    if not db_status:
        raise HTTPException(status_code=400, detail=_(locale, "status.not_exist"))
    
    db_invitation.status_name = db_status.name
    db_invitation.updated_by = currentUser['username']
    db_invitation.updated_date = datetime.now()
        
    try:
        db.add(db_invitation)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "invitation.already_exist"))
            
    