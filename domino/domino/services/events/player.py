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

from domino.models.events.player import Players

from domino.schemas.resources.result_object import ResultObject

from domino.services.resources.status import get_one_by_name, get_one as get_one_status
from domino.services.events.invitations import get_one_by_id as get_invitation_by_id
from domino.services.events.tourney import get_one as get_torneuy_by_eid, get_info_categories_tourney
from domino.services.events.domino_round import get_last_by_tourney, remove_configurate_round

from domino.services.enterprise.userprofile import get_one as get_one_profile

from domino.services.resources.utils import get_result_count
from domino.services.enterprise.auth import get_url_avatar

def new(request: Request, invitation_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_invitation = get_invitation_by_id(invitation_id=invitation_id, db=db)
    if not one_invitation:
        raise HTTPException(status_code=404, detail=_(locale, "invitation.not_found"))
    
    if one_invitation.status_name != 'ACCEPTED' and one_invitation.status_name != 'REFUTED':
        raise HTTPException(status_code=404, detail=_(locale, "invitation.status_incorrect"))
    
    status_end = get_one_by_name('FINALIZED', db=db)
    
    if one_invitation.tourney.status_id == status_end.id:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
        
    one_player = get_one_by_invitation_id(invitation_id, db=db)
    if one_player:
        raise HTTPException(status_code=404, detail=_(locale, "player.already_exist"))
    
    # devolver el elo, nivel y rbking el jugador...
    dict_player = get_info_of_player(one_invitation.profile_id, db=db)
    
    status_confirmed = get_one_by_name('CONFIRMED', db=db)    
    one_player = Players(id=str(uuid.uuid4()), tourney_id=one_invitation.tourney_id, 
                         profile_id=one_invitation.profile_id, invitation_id=one_invitation.id,
                         created_by=currentUser['username'], updated_by=currentUser['username'], status_id=status_confirmed.id)
    
    if dict_player:
        one_player.elo = dict_player['elo']
        one_player.ranking = dict_player['ranking']
        one_player.level = dict_player['level']
    
    # cambiar estado a la invitacion para que no salga mas en el listado de propuesta de jugadores
    status_confirmed = get_one_by_name('CONFIRMED', db=db)
    if status_confirmed:
        one_invitation.updated_by = currentUser['username']
        one_invitation.updated_date = datetime.now()
        one_invitation.status_name = status_confirmed.name
    else:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    # verificar el estado de la ultima ronda del torneo.
    # Despues de Iniciada, no hago nada. En cinfigurada o creada boor todo y pongo la ronda en estado creada.
    
    lst_round = get_last_by_tourney(one_invitation.tourney_id, db=db)
    if lst_round.status.name in ('CREATED', 'CONFIGURATED'):
        remove_configurate_round(lst_round.tourney_id, lst_round.id, db=db)
    
    try:
        db.add(one_player)
        db.add(one_invitation)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        return False
 
def reject_one_invitation(request: Request, invitation_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_invitation = get_invitation_by_id(invitation_id=invitation_id, db=db)
    if not one_invitation:
        raise HTTPException(status_code=404, detail=_(locale, "invitation.not_found"))
    
    if one_invitation.status_name != 'ACCEPTED':
        raise HTTPException(status_code=404, detail=_(locale, "invitation.status_incorrect"))
    
    status_created = get_one_by_name('FINALIZED', db=db)
    if one_invitation.tourney.status_id == status_created.id:
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
            
            status_created = get_one_by_name('FINALIZED', db=db)
            if db_player.tourney.status_id == status_created.id:
                raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
    
            status_canc = get_one_by_name('CANCELLED', db=db)
            
            db_player.status_id = status_canc.id
            
            db_player.updated_by = currentUser['username']
            db_player.updated_date = datetime.now()
            
            db.commit()
        else:
            raise HTTPException(status_code=404, detail=_(locale, "player.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail="No es posible eliminar")
    return result

def change_status_player(request: Request, player_id: str, status: str, db: Session):
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    # posibilidades son:
    # Jugando (Expulsado, Pausa)
    # Pausa (Jugando, Expulsado)
    # Aceptado (Cancelado)
    
    # el torneo no puede edstar finalizado y la ronda actual tienr que estar en estado creada.
    status_new = get_one_by_name(status, db=db)
    
    db_player = db.query(Players).filter(Players.id == player_id).first()
    if not db_player:
        raise HTTPException(status_code=404, detail=_(locale, "player.not_found"))
    
    if db_player.tourney.status.name == "FINALIZED":
        raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
    
    #puede que no existan rondas todavia
    last_round = get_last_by_tourney(db_player.tourney_id, db=db)
    if last_round:
        if last_round.status.name not in ('CREATED', 'CONFIGURATED'):
            raise HTTPException(status_code=404, detail=_(locale, "round.status_incorrect"))
    
    if db_player.status.name not in ('CONFIRMED', 'PLAYING', 'PAUSE'):
        raise HTTPException(status_code=404, detail=_(locale, "player.status_incorrect"))

    if status_new.name == 'EXPELLED':
        if db_player.status_id not in ('PLAYING', 'PAUSE'):
            raise HTTPException(status_code=404, detail=_(locale, "player.status_incorrect"))
        
    elif status_new.name == 'PAUSE':
        if db_player.status.name != 'PLAYING':
            raise HTTPException(status_code=404, detail=_(locale, "player.status_incorrect"))
        
    elif status_new.name == 'PLAYING':
        if db_player.status.name != 'PAUSE':
            raise HTTPException(status_code=404, detail=_(locale, "player.status_incorrect"))
        
    elif status_new.name == 'CANCELLED':
        if db_player.status.name != 'CONFIRMED':
            raise HTTPException(status_code=404, detail=_(locale, "player.status_incorrect"))
        
        
    
    db_player.status_id = status_new.id
    db_player.updated_by = currentUser['username']
    db_player.updated_date = datetime.now()
    
    try:
        db.commit() 
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail="No es posible eliminar")
    return result

def get_number_players_by_elo(request:Request, tourney_id:str, min_elo:float, max_elo:float, db:Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    db_tourney = get_torneuy_by_eid(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    str_query = "SELECT count(players.id) FROM events.players player " 
    
    status_canc = get_one_by_name('CANCELLED', db=db)
    
    str_where = "WHERE status_id != " + str(status_canc.id)
    str_where += " AND player.tourney_id = '" + tourney_id + "' "  +\
        "AND player.elo >= " + str(min_elo) + " AND player.elo <= " + str(max_elo)
    
    str_query += str_where
    result.data = db.execute(str_query).fetchone()[0]
    
    return result

def get_info_of_player(profile_id: str, db: Session):  
    
    one_profile = get_one_profile(profile_id, db=db)
    if not one_profile:
        return {}
    
    if one_profile.profile_type == 'SINGLE_PLAYER':
        one_info = one_profile.profile_single_player[0]
    elif one_profile.profile_type == 'PAIR_PLAYER':
        one_info = one_profile.profile_pair_player[0]
    elif one_profile.profile_type == 'TEAM_PLAYER':
        one_info = one_profile.profile_team_player[0]
    else:
        one_info = None
        
    return {'elo': one_info.elo, 'ranking': one_info.ranking, 'level': one_info.level} if one_info else {}

def get_all_players_by_elo(request:Request, page: int, per_page: int, tourney_id: str, min_elo: float, max_elo: float, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    db_tourney = get_torneuy_by_eid(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    status_canc = get_one_by_name('CANCELLED', db=db)
    
    str_from = "FROM events.players player " +\
        "inner join enterprise.profile_member pro ON pro.id = player.profile_id " +\
        "left join resources.city ON city.id = pro.city_id " + \
        "left join resources.country ON country.id = city.country_id " +\
        "join resources.entities_status sta ON sta.id = player.status_id "
        
    str_count = "Select count(*) " + str_from
    str_query = "SELECT players.id, pro.name as name, pro.photo, pro.id as profile_id, " +\
        "city.name as city_name, country.name as country_name, player.level, player.elo, " +\
        "player.ranking, player.ranking position_number, sta.id as status_id, " +\
        "sta.name as status_name, sta.description as status_description  " + str_from
        
    str_where = "WHERE pro.is_ready is True AND status_id != " + str(status_canc.id) 
    str_where += " AND player.tourney_id = '" + tourney_id + "' "  +\
        "AND player.elo >= " + str(min_elo) + " AND player.elo <= " + str(max_elo)
    
    str_count += str_where
    str_query += str_where

    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY player.elo DESC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db, api_uri=api_uri) for item in lst_data]
    
    return result

def get_lst_id_player_by_elo(tourney_id: str, modality:str, min_elo: float, max_elo: float, db: Session):  
    
    str_query = "SELECT player.id FROM events.players player join resources.entities_status sta ON sta.id = player.status_id "
    
    str_where = "WHERE player.tourney_id = '" + tourney_id + "' AND sta.name IN ('CONFIRMED', 'PLAYING', 'WAITING') " +\
        "AND player.elo >= " + str(min_elo) + " AND player.elo <= " + str(max_elo)
    
    str_query += str_where

    str_query += " ORDER BY player.elo DESC " 
    lst_data = db.execute(str_query)
    lst_players = []
    for item in lst_data:
        lst_players.append(item.id)
    
    return lst_players

def get_all_players_by_category(request:Request, page: int, per_page: int, category_id: str, criteria_key: str, 
                                criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    # si el torneo es automatico, ya lo saco de la scala directamente.
    
    dict_result = get_info_categories_tourney(category_id=category_id, db=db)
    if not dict_result:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.category_not_exist"))
    
    str_from = "FROM events.players player " +\
        "inner join enterprise.profile_member pro ON pro.id = player.profile_id " +\
        "left join resources.city ON city.id = pro.city_id " + \
        "left join resources.country ON country.id = city.country_id " +\
        "join resources.entities_status sta ON sta.id = player.status_id "
    
    tourney_is_init = True if dict_result['status_name'] == 'INITIADED' or dict_result['status_name'] == 'FINALIZED' else False
    if tourney_is_init:
        str_from += "LEFT JOIN events.domino_rounds_scale rscale ON rscale.player_id = player.id "   
    
    str_count = "Select count(*) " + str_from
    str_query = "SELECT player.id, pro.name as name, pro.photo, pro.id as profile_id, " +\
        "city.name as city_name, country.name as country_name, player.level, player.elo, player.ranking, " +\
        "sta.id as status_id, sta.name as status_name, sta.description as status_description "  
        
    if tourney_is_init:
        str_query += ", rscale.position_number " 
    else:
        str_query += ", player.elo, position_number " 

    str_query += str_from
    
    str_where = "WHERE pro.is_ready is True AND sta.name != 'CANCELLED' " 
    str_where += " AND player.tourney_id = '" + dict_result['tourney_id'] + "' " 
    
    if tourney_is_init:
        str_where += " AND rscale.category_id = '" + category_id + "' "
    else:
        str_where += "AND player.elo >= " + str(dict_result['elo_min']) + " AND player.elo <= " + str(dict_result['elo_max'])
        
    dict_query = {'username': " AND username = '" + criteria_value + "'"}
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    else:
        if criteria_key == 'username' and criteria_value:
            str_where += "AND pro.id IN (Select profile_id from enterprise.profile_users WHERE username ilike '%" + str(criteria_value) + "%')"
    
    str_count += str_where
    str_query += str_where
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    if tourney_is_init:
        str_query += " ORDER BY rscale.position_number ASC "
    else:
        str_query += " ORDER BY player.elo DESC "  
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db, api_uri=api_uri) for item in lst_data]
    
    return result
  
def get_all_players_by_tourney(request:Request, page: int, per_page: int, tourney_id: str, 
                               criteria_key: str, criteria_value: str, player_name: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    db_tourney = get_torneuy_by_eid(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    status_canc = get_one_by_name('CANCELLED', db=db)
    str_status = ''
    if criteria_key and criteria_key == 'status_id':
        str_status = " AND sta.name = 'CONFIRMED' " if criteria_value == '0' else " AND sta.name = 'PLAYING' " \
            if criteria_value == '1' else " AND sta.name = 'WAITING' " if criteria_value == '2' else \
            " AND sta.name = 'EXPELLED' " if criteria_value == '3' else " AND sta.name = 'PAUSE' " \
            if criteria_value == '4' else " AND sta.name = 'CANCELLED' " if criteria_value == '5' else ""
    
    if not str_status:  # no me paso estado, devolver todos menos los cancelados 
        str_status = "AND sta.name != '" + str(status_canc.name) + "' "     
           
    str_from = "FROM events.players player " +\
        "inner join enterprise.profile_member pro ON pro.id = player.profile_id " +\
        "left join resources.city ON city.id = pro.city_id " + \
        "left join resources.country ON country.id = city.country_id " +\
        "join resources.entities_status sta ON sta.id = player.status_id "
    
    str_count = "Select count(*) " + str_from
    str_query = "SELECT player.id, pro.name as name, pro.photo, pro.id as profile_id, " +\
        "city.name as city_name, country.name as country_name, player.level, player.elo, " +\
        "player.ranking, player.ranking position_number, sta.id as status_id, " +\
        "sta.name as status_name, sta.description as status_description " + str_from
    
    str_where = "WHERE pro.is_ready is True AND player.tourney_id = '" + tourney_id + "' " 
    
    if player_name:   
        str_where += " AND pro.name ilike '%" + player_name + "%' "
    
    str_where += str_status
        
    str_count += str_where
    str_query += str_where
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY player.elo DESC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db, api_uri=api_uri) for item in lst_data]
    
    return result

def create_dict_row(item, page, db: Session, api_uri):
    
    image = get_url_avatar(item['profile_id'], item['photo'], api_uri=api_uri)
    
    new_row = {'id': item['id'], 'name': item['name'], 
               'country': item['country_name'] if item['country_name'] else '', 
               'city_name': item['city_name'] if item['city_name'] else '',  
               'photo' : image, 'elo': item['elo'], 'ranking': item['ranking'], 'level': item['level'],
               'status_name': item['status_name'], 'status_description': item['status_description'],
               'status_id': item['status_id'], 'position_number': item.position_number}
    if page != 0:
        new_row['selected'] = False
    
    return new_row

def get_one_by_invitation_id(invitation_id: str, db: Session):  
    return db.query(Players).filter(Players.invitation_id == invitation_id).first()


def created_all_players(request:Request, tourney_id:str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    status_end = get_one_by_name('FINALIZED', db=db)
    if not status_end:
        return True
    
    db_tourney = get_torneuy_by_eid(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    if db_tourney.status_id == status_end.id:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
    
    status_confirmed = get_one_by_name('CONFIRMED', db=db)
    if not status_confirmed:
        return True
    
    str_invs = "Select invitation_id invitation_id from events.players Where tourney_id = '"
    str_invs_ind = "SELECT inv.id invitation_id FROM events.invitations inv " +\
        "JOIN enterprise.profile_member pro ON pro.id = inv.profile_id " +\
        "WHERE profile_type IN ('SINGLE_PLAYER', 'PAIR_PLAYER') and status_name = 'ACCEPTED' "
        
    str_query = str_invs_ind + "AND tourney_id = '" + str(db_tourney.id) + "' "
    str_query += " AND inv.id NOT IN (" + str_invs + " " + str(db_tourney.id) + "') "
    lst_data = db.execute(str_query).fetchall()
    
    for item in lst_data:
        one_invitation = get_invitation_by_id(invitation_id=item.invitation_id, db=db)
        if not one_invitation:
            continue
        
        dict_player = get_info_of_player(one_invitation.profile_id, db=db)
        one_player = Players(id=str(uuid.uuid4()), tourney_id=one_invitation.tourney_id, 
                         profile_id=one_invitation.profile_id, invitation_id=one_invitation.id,
                         created_by=currentUser['username'], updated_by=currentUser['username'], status_id=status_confirmed.id)
        
        if dict_player:
            one_player.elo = dict_player['elo']
            one_player.ranking = dict_player['ranking']
            one_player.level = dict_player['level']
        
        one_invitation.updated_by = currentUser['username']
        one_invitation.updated_date = datetime.now()
        one_invitation.status_name = status_confirmed.name
        
        db.add(one_player)
        db.add(one_invitation)
        
    try:
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        return False
    