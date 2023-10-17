import math
import uuid

from datetime import datetime
from fastapi import HTTPException, Request, UploadFile, File
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
import json
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.config.config import settings
from domino.app import _

from domino.models.events.tourney import Players
from domino.schemas.events.player import PlayerBase
from domino.schemas.resources.result_object import ResultObject

from domino.services.resources.status import get_one_by_name, get_one as get_one_status
from domino.services.events.invitations import get_one_by_id as get_invitation_by_id
from domino.services.enterprise.users import get_one_by_username
from domino.services.events.tourney import get_one as get_torneuy_by_eid

from domino.services.resources.utils import get_result_count
from domino.services.enterprise.auth import get_url_avatar

def new(request: Request, invitation_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_invitation = get_invitation_by_id(invitation_id=invitation_id, db=db)
    if not one_invitation:
        raise HTTPException(status_code=404, detail=_(locale, "invitation.not_found"))
    
    if one_invitation.status_name != 'ACCEPTED':
        raise HTTPException(status_code=404, detail=_(locale, "invitation.status_incorrect"))
    
    db_tourney = get_torneuy_by_eid(one_invitation.tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    status_created = get_one_by_name('CREATED', db=db)
    if db_tourney.status_id != status_created.id:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
        
    one_player = get_one_by_invitation_id(invitation_id, db=db)
    if one_player:
        raise HTTPException(status_code=404, detail=_(locale, "players.already_exist"))
    
    one_player = Players(id=str(uuid.uuid4()), tourney_id=one_invitation.tourney_id, 
                         profile_id=one_invitation.profile_id, nivel='NORMAL', invitation_id=one_invitation.id,
                         created_by=currentUser['username'], updated_by=currentUser['username'], is_active=True)
    # cambiar estado a la invitacion para que no salga mas en el listado de propuesta de jugadores
    status_confirmed = get_one_by_name('CONFIRMED', db=db)
    if status_confirmed:
        one_invitation.updated_by = currentUser['username']
        one_invitation.updated_date = datetime.now()
        one_invitation.status_name = status_confirmed.name
    else:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    # try:
    db.add(one_player)
    db.add(one_invitation)
    db.commit()
    return result
    # except (Exception, SQLAlchemyError) as e:
    #     return False
 
def reject_one_invitation(request: Request, invitation_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_invitation = get_invitation_by_id(invitation_id=invitation_id, db=db)
    if not one_invitation:
        raise HTTPException(status_code=404, detail=_(locale, "invitation.not_found"))
    
    if one_invitation.status_name != 'ACCEPTED':
        raise HTTPException(status_code=404, detail=_(locale, "invitation.status_incorrect"))
    
    db_tourney = get_torneuy_by_eid(one_invitation.tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    status_created = get_one_by_name('CREATED', db=db)
    if db_tourney.status_id != status_created.id:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
    
    status_confirmed = get_one_by_name('REFUTED', db=db)
    if status_confirmed:
        one_invitation.updated_by = currentUser['username']
        one_invitation.updated_date = datetime.now()
        one_invitation.status_name = status_confirmed.name
    else:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    try:
        db.add(one_invitation)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        return False
        
def remove_player(request: Request, player_id: str, db: Session):
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    try:
        db_player = db.query(Players).filter(Players.id == player_id).first()
        if db_player:
            
            db_tourney = get_torneuy_by_eid(db_player.tourney_id, db=db)
            if not db_tourney:
                raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
            
            status_created = get_one_by_name('CREATED', db=db)
            if db_tourney.status_id != status_created.id:
                raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
    
            db_player.is_active = False
            
            db_player.updated_by = currentUser['username']
            db_player.updated_date = datetime.now()
            
            db.commit()
        else:
            raise HTTPException(status_code=404, detail=_(locale, "player.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail="No es posible eliminar")
    return result
    
def get_all_players_by_tourney(request:Request, page: int, per_page: int, tourney_id: str, is_active: bool, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    db_tourney = get_torneuy_by_eid(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    # status_created = get_one_by_name('CREATED', db=db)
    # if db_tourney.status_id != status_created.id:
    #     raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
            
    str_from = "FROM events.players " +\
        "inner join enterprise.profile_member pro ON pro.id = players.profile_id " +\
        "inner join enterprise.profile_type prot ON prot.name = pro.profile_type " +\
        "left join resources.city ON city.id = pro.city_id " + \
        "left join resources.country ON country.id = city.country_id "
    
    dict_modality = {'Individual': "join enterprise.profile_single_player player ON player.profile_id = pro.id ",
                     'Parejas': "join enterprise.profile_pair_player player ON player.profile_id = pro.id ",
                     'Equipo': "join enterprise.profile_team_player player ON player.profile_id = pro.id "}
    
    str_from += dict_modality[db_tourney.modality]
       
    str_count = "Select count(*) " + str_from
    str_query = "SELECT players.id, pro.name as name, prot.description as profile_type, pro.photo, pro.id as profile_id, " +\
        "city.name as city_name, country.name as country_name, player.level, player.elo, player.ranking " + str_from
    
    str_where = "WHERE pro.is_ready is True and players.is_active is " + str(is_active) 
    str_where += " AND players.tourney_id = '" + tourney_id + "' " 
    
    dict_query = {'username': " AND username.username = '" + criteria_value + "'"}
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    else:
        if criteria_key == 'username':
            str_where += "AND pro.id IN (Select profile_id from enterprise.profile_users WHERE username = '" + str(criteria_value) + "')"
            
        else:
            str_where += dict_query[criteria_key] if criteria_value else "" 
            
    str_count += str_where
    str_query += str_where

    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY player.ranking ASC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db, api_uri=api_uri) for item in lst_data]
    
    return result

def create_dict_row(item, page, db: Session, api_uri):
    
    image = get_url_avatar(item['profile_id'], item['photo'], api_uri=api_uri)
    
    new_row = {'id': item['id'], 'name': item['name'], 
               'profile_type': item['profile_type'],  
               'country': item['country_name'], 'city_name': item['city_name'],  
               'photo' : image, 'elo': item['elo'], 'ranking': item['ranking'], 'level': item['level']}
    if page != 0:
        new_row['selected'] = False
    
    return new_row

def get_one_by_invitation_id(invitation_id: str, db: Session):  
    return db.query(Players).filter(Players.invitation_id == invitation_id).first()