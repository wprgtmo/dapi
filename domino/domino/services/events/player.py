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

from domino.models.enterprise.userprofile import SingleProfile
from domino.models.events.player import Players, PlayersUser
from domino.models.events.invitations import Invitations

from domino.schemas.resources.result_object import ResultObject, ResultData
from domino.schemas.events.player import PlayerRegister, PlayerEloBase, PlayerUpdatedRegister

from domino.services.enterprise.profiletype import get_one_by_name as get_profile_type_by_name
from domino.services.resources.status import get_one_by_name, get_one as get_one_status
from domino.services.events.invitations import get_one_by_id as get_invitation_by_id
from domino.services.events.tourney import get_one as get_torneuy_by_eid, get_info_categories_tourney
from domino.services.events.domino_round import get_last_by_tourney, remove_configurate_round
from domino.services.enterprise.users import new_from_register, get_one as get_one_user_by_id
from domino.services.enterprise.comunprofile import new_profile
from domino.services.resources.city import get_one as city_get_one
from domino.services.resources.country import get_one as country_get_one

from domino.services.enterprise.userprofile import get_one as get_one_profile, get_one_single_profile_by_id, get_one_default_user, get_type_level

from domino.services.resources.utils import get_result_count, create_dir, del_image, get_ext_at_file, upfile
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
    
    status_confirmed = get_one_by_name('CONFIRMED', db=db)  
    if not status_confirmed:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    one_player = new_player_with_user(one_invitation.tourney_id, one_invitation.profile_id, one_invitation.id,
                                      currentUser['username'], status_confirmed.id, db=db) 
    
    if not one_player:
        raise HTTPException(status_code=404, detail=_(locale, "player.profile_not_found"))
    
    # cambiar estado a la invitacion para que no salga mas en el listado de propuesta de jugadores
    one_invitation.updated_by = currentUser['username']
    one_invitation.updated_date = datetime.now()
    one_invitation.status_name = status_confirmed.name
        
    
    # verificar el estado de la ultima ronda del torneo.
    # Despues de Iniciada, no hago nada. En configurada o creada borrar todo y pongo la ronda en estado creada.
    
    restar_round(one_invitation.tourney_id, db=db)
    
    try:
        db.add(one_player)
        db.add(one_invitation)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        return False

def new_player_with_user(tourney_id, profile_id, invitation_id, created_by, status_id, db:Session):
    
    one_player = Players(id=str(uuid.uuid4()), tourney_id=tourney_id, profile_id=profile_id, 
                         invitation_id=invitation_id, created_by=created_by, updated_by=created_by, 
                         status_id=status_id)
    
    # devolver el elo, nivel el jugador...
    dict_player = get_info_of_player(profile_id, db=db)
    
    if dict_player:
        
        if dict_player['profile_type'] == 'SINGLE_PLAYER':
            level_name = get_type_level(dict_player['level']) if dict_player['level'] else '' 
            
            one_player.elo = dict_player['elo']
            one_player.level = level_name
    
            one_player_user =  PlayersUser(
                player_id=one_player.id, profile_id=profile_id, level=one_player.level,
                elo=one_player.elo, elo_current=0, elo_at_end=0, games_played=0, games_won=0, games_lost=0,
                points_positive=0, points_negative=0, points_difference=0, score_expected=0, score_obtained=0,
                k_value=0, penalty_yellow=0, penalty_red=0, penalty_total=0, bonus_points=0)
            one_player.users.append(one_player_user)
            
        elif dict_player['profile_type'] == 'PAIR_PLAYER': 
            pass
        elif dict_player['profile_type'] == 'TEAM_PLAYER': 
            pass
        else:
            return None
    else:
        return None
    
    return one_player

#metodo para registrar un nuevo jugador, creandolo desde el usuario
def register_new_player(request: Request, tourney_id: str, player_register: PlayerRegister, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_tourney = get_torneuy_by_eid(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    if db_tourney.status.name == 'FINALIZED':
        raise HTTPException(status_code=404, detail=_(locale, "tourney.status_incorrect"))
    
    country = None
    one_city = city_get_one(city_id=player_register.city_id, db=db)
    if one_city:
        country = one_city.country
    else:
        if player_register.country_id:
            country = country_get_one(player_register.country_id, db=db)
    
    if  not player_register.username:
        raise HTTPException(status_code=404, detail=_(locale, "player.username_is_requeied"))
    
    if  not player_register.first_name:
        raise HTTPException(status_code=404, detail=_(locale, "player.first_name_is_requeied"))
    
    if  not player_register.email:
        raise HTTPException(status_code=404, detail=_(locale, "player.email_is_requeied"))
    
    if not player_register.level:
        raise HTTPException(status_code=404, detail=_(locale, "player.level_is_requeied"))
    
    if not player_register.elo:
        raise HTTPException(status_code=404, detail=_(locale, "player.elo_is_requeied"))
    
    db_user = new_from_register(player_register.email, player_register.username, player_register.first_name,
                      player_register.last_name, player_register.alias, player_register.phone, 
                      one_city, country, currentUser['username'], None, db=db, locale=locale)
   
    name = player_register.first_name + ' ' + player_register.last_name if player_register.last_name \
        else player_register.first_name if player_register.first_name else '' 
    create_new_single_player(db_tourney, player_register.username, name, player_register.email, one_city, 
                             player_register.elo, player_register.level, currentUser['username'], None, db=db,
                             profile_user_id=db_user.id)
    
    # debo siempre comprobar el estado de la ultima ronda y en dependenca desu estado, reiniciar
    restar_round(db_tourney.id, db=db)
    
    try:
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        return False

def update_register_one_player(request: Request, player_id: str, player_register: PlayerRegister, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_player = get_one(player_id, db=db)
    if not db_player:
        raise HTTPException(status_code=404, detail=_(locale, "player.not_found"))
    
    db_player.elo = player_register.elo
    db_player.level = player_register.level
    
    one_profile = get_one_single_profile_by_id(db_player.profile_id, db=db)
    if not one_profile:
        raise HTTPException(status_code=404, detail=_(locale, "player.not_found"))
    
    # buscar su perfil y cambiar los datos
    db_user = get_one_default_user(one_profile.profile_user_id, db=db)
    
    if one_profile.profile.email != player_register.email:
        one_profile.profile.email = player_register.email
        db.add(one_profile.profile)
        
    if one_profile.level != player_register.email:
        one_profile.level = player_register.level
        db.add(one_profile)
    
    if db_user.alias != player_register.alias:
        db_user.alias = player_register.alias
        db.add(db_user)
        
    one_user = get_one_user_by_id(db_user.profile_id, db=db)
    if one_user.first_name != player_register.first_name:
        one_user.first_name = player_register.first_name
        
    if one_user.last_name != player_register.last_name:
        one_user.last_name = player_register.last_name
        
    if one_user.email != player_register.email:
        one_user.email = player_register.email
        
    if one_user.phone != player_register.phone:
        one_user.phone = player_register.phone
    
    # buscarlo en la tabla de jugadores y actualizar estos datos
    str_update = "Update events.players_users pu SET elo = " + str(float(player_register.elo)) + ", level = '" +\
        player_register.level + "' FROM events.players pa WHERE pa.id = pu.player_id " +\
        " AND pa.tourney_id = '" + db_player.tourney_id + "' and pu.profile_id = '" + db_player.profile_id + "'; COMMIT; "
      
    try:
        db.execute(str_update)  
        db.add(one_user)
        db.add(db_player)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        result.success = False
        return result

def get_info_one_player(request: Request, player_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    db_player = get_one(player_id, db=db)
    if not db_player:
        raise HTTPException(status_code=404, detail=_(locale, "player.not_found"))
    
    str_query = "SELECT users.username, users.first_name, users.last_name, enterprise.profile_default_user.alias, " +\
        "users.email, users.phone, profile_single_player.elo, enterprise.profile_member.city_id, " +\
        "enterprise.users.country_id, profile_single_player.level " +\
        "FROM enterprise.profile_member " +\
        "join enterprise.profile_users ON profile_users.profile_id = profile_member.id " +\
        "join enterprise.profile_single_player ON profile_single_player.profile_id = profile_member.id " +\
        "join enterprise.users ON users.id = profile_single_player.profile_user_id " + \
        "join enterprise.profile_default_user ON profile_default_user.profile_id = users.id " + \
        "WHERE profile_member.id='" + db_player.profile_id + "' "
    dat_result = db.execute(str_query).fetchone()
    if dat_result:
        db_register = PlayerRegister(username=dat_result.username, first_name=dat_result.first_name if dat_result.first_name else dat_result.username, 
                                     last_name=dat_result.last_name if dat_result.last_name else '',
                                     alias=dat_result.alias if dat_result.alias else '', 
                                     email=dat_result.email if dat_result.email else  dat_result.username + '@gmail.com', 
                                     phone=dat_result.phone if dat_result.phone else '',
                                     city_id=dat_result.city_id if dat_result.city_id else '1', 
                                     country_id=dat_result.country_id if dat_result.country_id else '1', 
                                     elo=dat_result.elo if dat_result.elo else 0, level=dat_result.level if dat_result.level else 'rookie')
        result.data = db_register
    
    try:
        return result
    except (Exception, SQLAlchemyError) as e:
        return False

def create_new_single_player(db_tourney, username, name, email, city, elo, level, created_by, file, db: Session,
                             profile_user_id:str=None):
    
    profile_type = get_profile_type_by_name("SINGLE_PLAYER", db=db)
    if not profile_type:
        return True
    
    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, id, username, name, email, city.id if city else None, True, True, True, 
                              "USERPROFILE", created_by, created_by, file, is_confirmed=True, single_profile_id=id)
    
    level = 'rookie' if not level else level
    one_single_player = SingleProfile(profile_id=id, elo=elo, level=level, updated_by=created_by, profile_user_id=profile_user_id)
    one_profile.profile_single_player.append(one_single_player)
    
    status_acc = get_one_by_name('ACCEPTED', db=db)
    
    one_invitation = Invitations(id=str(uuid.uuid4()), tourney_id=db_tourney.id, profile_id=id, modality=db_tourney.modality,
                                 status_name=status_acc.name, created_by=created_by, updated_by=created_by)
            
    status_confirmed = get_one_by_name('CONFIRMED', db=db) 
    one_player = Players(id=str(uuid.uuid4()), tourney_id=db_tourney.id, profile_id=id, 
                         invitation_id=one_invitation.id, created_by=created_by, updated_by=created_by, 
                         status_id=status_confirmed.id, elo=elo, level=level)
    
    one_player_user =  PlayersUser(
        player_id=one_player.id, profile_id=id, level=one_player.level,
        elo=one_player.elo, elo_current=0, elo_at_end=0, games_played=0, games_won=0, games_lost=0,
        points_positive=0, points_negative=0, points_difference=0, score_expected=0, score_obtained=0,
        k_value=0, penalty_yellow=0, penalty_red=0, penalty_total=0, bonus_points=0)
    one_player.users.append(one_player_user)
        
    try:   
        db.add(one_profile)
        db.add(one_invitation)
        db.add(one_player)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        return True

def update_image_one_player(request: Request, player_id: str, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    db_player = get_one(player_id, db=db)
    if not db_player:
        raise HTTPException(status_code=404, detail=_(locale, "player.not_found"))
    
    path_player = create_dir(entity_type="USERPROFILE", user_id=None, entity_id=str(db_player.profile_id))
    
    #puede venir la foto o no venir y eso es para borrarla.
    if db_player.profile_member.photo:  # ya tiene una imagen asociada
        current_image = db_player.profile_member.photo
        try:
            del_image(path=path_player, name=str(current_image))
        except:
            pass
    
    if not file:
        db_player.profile_member.photo = None
    else:   
        ext = get_ext_at_file(file.filename)
        file.filename = str(uuid.uuid4()) + "." + ext
        
        upfile(file=file, path=path_player)
        db_player.profile_member.photo = file.filename
    
    try:
        db.add(db_player.profile_member)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "tourney.already_exist"))
            
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
            
            restar_round(db_player.tourney_id, db=db)
            
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

def restar_round(tourney_id:str, db:Session):
    
    lst_round = get_last_by_tourney(tourney_id, db=db)
    
    if lst_round and lst_round.status.name in ('CREATED', 'CONFIGURATED'):
        remove_configurate_round(lst_round.tourney_id, lst_round.id, db=db)
    return True

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
        
    return {'elo': one_info.elo, 'level': one_info.level, 'profile_type': one_profile.profile_type} if one_info else {}

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
        "city.name as city_name, country.name as country_name, player.level, player.elo "
    
    str_where = "WHERE ready is True AND status_id != " + str(status_canc.id) 
    str_where += " AND player.tourney_id = '" + tourney_id + "' "  +\
        "AND player.elo >= " + str(min_elo) + " AND player.elo <= " + str(max_elo)
    
    str_count += str_where
    str_query += str_where

    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY player.elo DESC, pro.name ASC " 
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

    str_query += " ORDER BY player.elo DESC, player.id ASC " 
    lst_data = db.execute(str_query)
    lst_players = []
    for item in lst_data:
        lst_players.append(item.id)
    
    return lst_players

def get_lst_id_player_by_level(tourney_id: str, modality:str, category_id: str, db: Session):  
    
    str_query = "SELECT player_id id FROM events.players_users pu " +\
        "JOIN events.players pp ON pp.id = pu.player_id " +\
        "join resources.entities_status sta ON sta.id = pp.status_id " +\
        "WHERE pp.tourney_id = '" + tourney_id + "' AND sta.name IN ('CONFIRMED', 'PLAYING', 'WAITING') " +\
        "AND pu.category_id = '" + category_id + "'"
    
    str_query += " ORDER BY pp.elo DESC, pp.id ASC " 
    lst_data = db.execute(str_query)
    lst_players = []
    for item in lst_data:
        lst_players.append(item.id)
    
    return lst_players
    
def get_lst_id_player_with_boletus(tourney_id: str, db: Session):  
    
    str_query = "SELECT player.id FROM events.players player join resources.entities_status sta ON sta.id = player.status_id "
    
    str_where = "WHERE player.tourney_id = '" + tourney_id + "' AND sta.name IN ('CONFIRMED', 'PLAYING', 'WAITING') " 
    
    str_query += str_where

    str_query += " ORDER BY player.elo DESC, pro.name ASC " 
    lst_data = db.execute(str_query)
    lst_players = []
    for item in lst_data:
        lst_players.append(item.id)
    
    return lst_players

def get_all_players_by_category(request:Request, page: int, per_page: int, category_id: str, criteria_key: str, 
                                criteria_value: str, db: Session, tourney_id=None):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    # Si no viene categorias debo devolver todos los jugadores
    
    # si el torneo es automatico, ya lo saco de la scala directamente.
    dict_result, lottery_type = {}, ""
    if category_id:
        dict_result = get_info_categories_tourney(category_id=category_id, db=db)
        if not dict_result:
            raise HTTPException(status_code=404, detail=_(locale, "tourney.category_not_exist"))
        tourney_id = dict_result['tourney_id']
        lottery_type = dict_result['lottery_type']
    else:
        db_tourney = get_torneuy_by_eid(tourney_id, db=db)
        if not db_tourney:
            raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
        lottery_type = db_tourney.lottery_type
    
    if lottery_type == 'AUTOMATIC':
        round_config = True
    else:
        # buscar la ultima ronda del torneo y en dependecia de su estado saco de una tabla o de la otra...
        lst_round = get_last_by_tourney(tourney_id, db=db)
        round_config = False if lst_round.status.name == "CREATED" else True
     
    str_from = "FROM events.players player " +\
        "inner join events.players_users pu ON pu.player_id = player.id " +\
        "inner join enterprise.profile_member pro ON pro.id = player.profile_id " +\
        "left join resources.city ON city.id = pro.city_id " + \
        "left join resources.country ON country.id = city.country_id " +\
        "join resources.entities_status sta ON sta.id = player.status_id "
    
    if round_config:
        str_from += "LEFT JOIN events.domino_rounds_scale rscale ON rscale.player_id = player.id "   
    
    str_count = "Select count(*) " + str_from
    str_query = "SELECT player.id, pro.name as name, pro.photo, pro.id as profile_id, " +\
        "city.name as city_name, country.name as country_name, player.level, player.elo, " +\
        "sta.id as status_id, sta.name as status_name, sta.description as status_description "  
        
    if round_config:
        str_query += ", rscale.position_number " 
    else:
        str_query += ", player.elo, '' as position_number " 

    str_query += str_from
    
    str_where = "WHERE pro.is_ready is True AND sta.name not in ('CANCELLED', 'EXPELLED') " 
    str_where += " AND player.tourney_id = '" + tourney_id + "' " 
    
    if dict_result['segmentation_type'] == 'ELO':
        if round_config:
            str_where += " AND rscale.category_id = '" + category_id + "' " if category_id else ""
        else:
            str_where += "AND player.elo >= " + str(dict_result['elo_min']) + " AND player.elo <= " + str(dict_result['elo_max']) if category_id else ""
    else:
        str_where += " AND pu.category_id = '" + category_id + "' " if category_id else ""
              
    dict_query = {'username': " AND username = '" + criteria_value + "'"}
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    else:
        if criteria_key == 'username' and criteria_value:
            str_where += "AND pro.name ilike '%" + str(criteria_value) + "%'"
    
    str_count += str_where
    str_query += str_where
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    if round_config:
        str_query += " ORDER BY rscale.position_number ASC "
    else:
        str_query += " ORDER BY player.elo DESC, pro.name ASC "  
    
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
        str_status = " AND sta.name = 'CONFIRMED' " if criteria_value == '1' else " AND sta.name = 'PLAYING' " \
            if criteria_value == '2' else " AND sta.name = 'WAITING' " if criteria_value == '3' else \
            " AND sta.name = 'EXPELLED' " if criteria_value == '4' else " AND sta.name = 'PAUSE' " \
            if criteria_value == '5' else " AND sta.name = 'CANCELLED' " if criteria_value == '6' else ""
    
    if not str_status:  # no devolver nada
        result = ResultData(page=page, per_page=per_page)  
        result.total 
        result.data = []
        return result
        # str_status = "AND sta.name != '" + str(status_canc.name) + "' "     
           
    str_from = "FROM events.players player " +\
        "inner join enterprise.profile_member pro ON pro.id = player.profile_id " +\
        "left join resources.city ON city.id = pro.city_id " + \
        "left join resources.country ON country.id = city.country_id " +\
        "join resources.entities_status sta ON sta.id = player.status_id " +\
        'LEFT JOIN enterprise.profile_single_player player_sing ON player_sing.profile_id = pro.id ' +\
        "JOIN federations.clubs club ON club.id = player_sing.club_id "
    
    str_count = "Select count(*) " + str_from
    str_query = "SELECT player.id, pro.name as name, pro.photo, pro.id as profile_id, " +\
        "city.name as city_name, country.name as country_name, player.level, player.elo, " +\
        " '' as position_number, sta.id as status_id, " +\
        "sta.name as status_name, sta.description as status_description, club.name as club_name " + str_from
    
    str_where = "WHERE pro.is_ready is True AND player.tourney_id = '" + tourney_id + "' " 
    
    if player_name:   
        str_where += " AND pro.name ilike '%" + player_name + "%' "
    
    str_where += str_status
        
    str_count += str_where
    str_query += str_where
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY player.elo DESC, pro.name ASC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, page, db=db, api_uri=api_uri) for item in lst_data]
    
    return result

def create_dict_row(item, page, db: Session, api_uri):
    
    image = get_url_avatar(item['profile_id'], item['photo'], api_uri=api_uri)
    level_name = get_type_level(item['level']) if item.level else '' 
    
    new_row = {'id': item['id'], 'name': item['name'], 
               'country': item['country_name'] if item['country_name'] else '', 
               'city_name': item['city_name'] if item['city_name'] else '',  
               'photo' : image, 'elo': item['elo'], 'level': level_name,
               'status_name': item['status_name'], 'status_description': item['status_description'],
               'status_id': item['status_id'], 'club_name': item.club_name,
               'position_number': item.position_number}
   
    return new_row

def get_one_by_invitation_id(invitation_id: str, db: Session):  
    return db.query(Players).filter(Players.invitation_id == invitation_id).first()

def get_one(id: str, db: Session):  
    return db.query(Players).filter(Players.id == id).first()

def get_one_user(player_id: str, profile_id: str, db: Session):  
    return db.query(PlayersUser).filter(PlayersUser.player_id == player_id).\
        filter(PlayersUser.profile_id == profile_id).first()

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
        
        one_player = new_player_with_user(one_invitation.tourney_id, one_invitation.profile_id, one_invitation.id,
                                        currentUser['username'], status_confirmed.id, db=db) 
    
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
    
def change_status_player_at_init_round(request:Request, db_round, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    return change_all_status_player_at_init_round(db_round, db=db)
    
def change_all_status_player_at_init_round(db_round, db: Session):
    
    result = ResultObject() 
    
    str_query_pair = "Select sca_one.player_id as one_player_id, sca_two.player_id as  two_player_id " +\
        "from events.domino_rounds_pairs pa " +\
        "join events.domino_rounds_scale sca_one ON sca_one.id = pa.scale_id_one_player " +\
        "join events.domino_rounds_scale sca_two ON sca_two.id = pa.scale_id_two_player " +\
        "Where pa.round_id = '" + db_round.id + "' "
        
    lst_pair = []
    lst_all_id = db.execute(str_query_pair).fetchall()
    str_id_playing = "'"
    for item in lst_all_id:
        str_id_playing += item.one_player_id + "','" + item.two_player_id + "','"
        lst_pair.append(item.one_player_id)
        lst_pair.append(item.two_player_id)
     
    # obtener lista de jugadores del torneo en cualquier estado
    lst_player = get_lst_id_player_by_elo(db_round.tourney_id, db_round.tourney.modality, db_round.tourney.elo_min, db_round.tourney.elo_max, db=db)
    str_waiting = "'"
    
    for item in lst_player:
        if item not in str_id_playing:
            str_waiting += item + "','"
 
    status_play = get_one_by_name('PLAYING', db=db)
    status_wait = get_one_by_name('WAITING', db=db)
    
    if str_id_playing != "'":
        str_update_playing = "UPDATE events.players SET status_id = " + str(status_play.id) + " WHERE id IN (" + str_id_playing[:-2] + ");COMMIT;"  
        db.execute(str_update_playing)
    if str_waiting != "'":
        str_update_waiting = "UPDATE events.players SET status_id = " + str(status_wait.id) + " WHERE id IN (" + str_waiting[:-2] + ");COMMIT;"  
        db.execute(str_update_waiting)
    
    db.commit()
    
    return result