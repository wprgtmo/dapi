import math
from datetime import datetime

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
from domino.services.player import new_player
from domino.services.referee import new_referee
from domino.services.users import get_one_by_username
from domino.services.status import get_one_by_name as get_status_by_name

def get_one_by_id(invitation_id: str, db: Session):  
    return db.query(Invitations).filter(Invitations.id == invitation_id).first()
           
def get_all_by_tourney(tourney_id: str, db: Session):  
    return db.query(Invitations).filter(Invitations.tourney_id == tourney_id).all()

# def get_all_sent_by_user(request, db: Session):  
    
#     currentUser = get_current_user(request)
    
#     return get_invitations_by_user_and_status(user_name=currentUser['username'], status_name='SEND', result=ResultObject(), db=db)

# def get_all_accept_by_user(request, db: Session):  
    
#     currentUser = get_current_user(request)
    
#     return get_invitations_by_user_and_status(user_name=currentUser['username'], status_name='ACCEPTED', result=ResultObject(), db=db)

def get_all_invitations_by_user(request, status_name:str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    str_query = "SELECT invitations.id, tourney.name as tourney_name, tourney.modality, tourney.start_date, " + \
        "events.name as event_name, events.close_date, events.main_location, city.name as city_name, " + \
        "country.name country_name, eve.description as rolevent_name " +\
        "FROM events.invitations " + \
        "inner join events.tourney ON tourney.id = invitations.tourney_id " + \
        "inner join events.events ON events.id = tourney.event_id " + \
        "inner join resources.event_roles eve ON eve.name = invitations.rolevent_name " +\
        "left join resources.city ON city.id = events.city_id " +\
        "left join resources.country ON country.id = city.country_id " +\
        "WHERE user_name = '" + currentUser['username'] + "' "
        
    if status_name != 'ALL':
        str_query += " AND invitations.status_name = '" + status_name + "' "
        
    str_query += "ORDER BY tourney.start_date ASC "
        
    lst_inv = db.execute(str_query)
    result.data = [create_dict_row_invitation(item) for item in lst_inv]
    
    return result
 
def create_dict_row_invitation(item):
    
    summary = "Se le invita a participar en el Evento: " + str(item['event_name']) 
    summary += " en calidad de  " + str(item['rolevent_name'])  + ","
    summary += " a celebrarse en: " + str(item['country_name']) + ","
    summary += " en la ciudad de: " + str(item['city_name']) + "," if item['city_name'] else ""
    summary += " con sede principal en: " + str(item['main_location']) + ", " if item['main_location'] else ""
    summary += " en el torneo: " + str(item['tourney_name']) + "," if item['tourney_name'] else ""
    summary += " en la modalidad: " + str(item['modality']) if item['modality'] else ""
    summary += " desde el " + item['start_date'].strftime('%d/%m/%Y') + " hasta " + item['close_date'].strftime('%d/%m/%Y')
    
    new_row = {'id': item['id'], 'summary': summary, 'selected': False}
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
        
    str_users = "SELECT users.username, eve.name as rolevent_name FROM enterprise.users " + \
        "inner join enterprise.user_eventroles everol ON everol.username = users.username " +\
        "inner join resources.event_roles eve ON eve.id = everol.eventrol_id " +\
        "where users.is_active = True and receive_notifications = True " +\
        "and users.username in (Select username FROM enterprise.user_eventroles inner join resources.event_roles rol " +\
        "ON rol.id = user_eventroles.eventrol_id where name IN ('PLAYER', 'REFEREE')) " +\
        "and users.username NOT IN (Select user_name FROM events.invitations where tourney_id = '" + tourney_id + "') "

    lst_data = db.execute(str_users)
    
    try:
        for item in lst_data:
            one_invitation = Invitations(tourney_id=db_tourney.id, user_name=item.username, 
                                         rolevent_name=item.rolevent_name, status_name=db_status.name,
                                         created_by=currentUser['username'], updated_by=currentUser['username'])
            db.add(one_invitation)
            db.commit()
        
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
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
    
    status_name = 'ACCEPTED' if invitation.accept else 'REJECTED'
    db_status = get_status_by_name(status_name, db=db)
    if not db_status:
        raise HTTPException(status_code=400, detail=_(locale, "status.not_exist"))
    
    db_invitation.status_name = db_status.name
    db_invitation.updated_by = currentUser['username']
    db_invitation.updated_date = datetime.now()
    
    if status_name == 'ACCEPTED':  #inscribir como jugador o arbitro
        one_user = get_one_by_username(db_invitation.user_name, db=db)
        
        if db_invitation.rolevent_name == 'PLAYER':
            result_update = new_player(tourney_id=db_invitation.tourney_id, user_id=one_user.id, 
                                username=db_invitation.user_name, db=db)
        elif db_invitation.rolevent_name == 'REFEREE':
            result_update = new_referee(tourney_id=db_invitation.tourney_id, user_id=one_user.id, 
                                 username=db_invitation.user_name, db=db)
    
        if not result_update:
            raise HTTPException(status_code=400, detail=_(locale, "invitation.error_create_player"))
        
    try:
        db.add(db_invitation)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "invitation.already_exist"))
            
    