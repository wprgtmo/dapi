import math
import uuid

from datetime import datetime

from domino.config.config import settings
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.app import _

from domino.models.resources.status import StatusElement
from domino.models.events.inscriptions import Inscriptions

from domino.schemas.events.inscriptions import InscriptionsBase, InscriptionsCreated, InscriptionsUpdated
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.utils import get_result_count
from domino.services.events.tourney import get_one as get_tourney_by_id
from domino.services.enterprise.users import get_one_by_username
from domino.services.resources.status import get_one_by_name as get_status_by_name
from domino.services.resources.country import get_one_by_name as get_country_by_name
from domino.services.enterprise.userprofile import get_type_level, get_one as get_one_profile
from domino.services.events.player import new_player_from_inscription

from domino.services.enterprise.auth import get_url_avatar

def get_one(inscriptions_id: str, db: Session):  
    return db.query(Inscriptions).filter(Inscriptions.id == inscriptions_id).first()

def get_one_by_id(request:Request, inscriptions_id: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject()  
    
    api_uri = str(settings.api_uri)
    
    db_one_inscription = get_one(inscriptions_id, db=db)
    if not db_one_inscription:
        raise HTTPException(status_code=400, detail=_(locale, "inscriptions.not_found"))
    
    str_from = "FROM events.inscriptions ins " +\
        "JOIN enterprise.profile_member pm ON pm.id = ins.profile_id " 
        
    if db_one_inscription.modality == 'Individual':
        str_from += "JOIN enterprise.profile_single_player pp ON pp.profile_id = pm.id "
    elif db_one_inscription.modality == 'Parejas':
        str_from += "JOIN enterprise.profile_pair_player pp ON pp.profile_id = pm.id "
    else:
        raise HTTPException(status_code=400, detail=_(locale, "tourney.not_implemented"))
    
    str_from += "JOIN federations.clubs club ON club.id = pp.club_id " +\
        "JOIN federations.federations ON federations.id = club.federation_id "
    
    str_query = "Select ins.profile_id, pm.name, was_pay, payment_way, import_pay, pm.photo, pp.elo, pp.level, " +\
        "club.name as club_name, federations.name as federation_name " + str_from + " WHERE ins.id = '" + inscriptions_id + "' "
    one_data = db.execute(str_query).fetchone()
    
    result.data = {'profile_id': one_data.profile_id, 'name': one_data['name'], 
               'was_pay': one_data['was_pay'], 'payment_way': one_data['payment_way'] if one_data['payment_way'] else '', 
               'import_pay': one_data['import_pay'] if one_data['import_pay'] else '0.00', 
               'elo': one_data['elo'], 'level': one_data['level'] if one_data['level'] else '', 
               'club_name': one_data['club_name'] if one_data['club_name'] else '', 
               'federation_name': one_data['federation_name'] if one_data['federation_name'] else '',
               'photo' : get_url_avatar(one_data['profile_id'], one_data['photo'], api_uri=api_uri)}
    
    return result

def get_all(request:Request, tourney_id:str, page: int, per_page: int, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    db_one_tourney = get_tourney_by_id(tourney_id, db=db)
    if not db_one_tourney:
        raise HTTPException(status_code=400, detail=_(locale, "tourney.not_found"))
    
    str_from = "FROM events.inscriptions ins " +\
        "JOIN enterprise.profile_member pm ON pm.id = ins.profile_id " 
        
    if db_one_tourney.modality == 'Individual':
        str_from += "JOIN enterprise.profile_single_player pp ON pp.profile_id = pm.id "
    elif db_one_tourney.modality == 'Parejas':
        str_from += "JOIN enterprise.profile_pair_player pp ON pp.profile_id = pm.id "
    else:
        raise HTTPException(status_code=400, detail=_(locale, "tourney.not_implemented"))
    
    str_from += "JOIN federations.clubs club ON club.id = pp.club_id " +\
        "JOIN federations.federations ON federations.id = club.federation_id "  
                
    str_count = "Select count(*) " + str_from
    str_query = "Select ins.profile_id, pm.name, was_pay, payment_way, import_pay, pm.photo, pp.elo, pp.level, " +\
        "club.name as club_name, federations.name as federation_name " + str_from
    
    str_where = " WHERE ins.status_name != 'CANCELLED' AND tourney_id = '" + tourney_id + "' "  
    
    str_search = ''
    if criteria_value:
        str_search = "AND (pm.name ilike '%" + criteria_value + "%' OR ins.payment_way ilike '%" + criteria_value +\
            "%' OR pp.level ilike '%" + criteria_value + "%' OR club.name ilike '%" + criteria_value +\
            "%' OR federations.name ilike '%" + criteria_value + "%')"
        str_where += str_search
        
    str_count += str_where
    str_query += str_where
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY pm.name DESC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_invitation(item, api_uri=api_uri) for item in lst_data]
    
    return result

def create_dict_row_invitation(item, api_uri=""):
    
    dict_row = {'profile_id': item['profile_id'], 'name': item['name'], 
               'was_pay': item['was_pay'], 'payment_way': item['payment_way'] if item['payment_way'] else '', 
               'import_pay': item['import_pay'] if item['import_pay'] else '0.00', 
               'elo': item['elo'], 'level': item['level'] if item['level'] else '', 
               'club_name': item['club_name'] if item['club_name'] else '', 
               'federation_name': item['federation_name'] if item['federation_name'] else '',
               'photo' : get_url_avatar(item['profile_id'], item['photo'], api_uri=api_uri)}
    
    return dict_row

def get_all_players_not_registered(request:Request, tourney_id:str, page: int, per_page: int, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    db_one_tourney = get_tourney_by_id(tourney_id, db=db)
    if not db_one_tourney:
        raise HTTPException(status_code=400, detail=_(locale, "tourney.not_found"))
    
    str_from = "FROM enterprise.profile_member pm " 
    
    if db_one_tourney.modality == 'Individual':
        str_from += "JOIN enterprise.profile_single_player pp ON pp.profile_id = pm.id "
    elif db_one_tourney.modality == 'Parejas':
        str_from += "JOIN enterprise.profile_pair_player pp ON pp.profile_id = pm.id "
    else:
        raise HTTPException(status_code=400, detail=_(locale, "tourney.not_implemented"))
    
    str_from += "JOIN federations.clubs club ON club.id = pp.club_id " +\
        "JOIN federations.federations ON federations.id = club.federation_id "  
                
    str_count = "Select count(*) " + str_from
    str_query = "Select pm.id as profile_id, pm.name, pm.photo, pp.elo, pp.level, " +\
        "club.name as club_name, federations.name as federation_name " + str_from
   
    str_ins = "Select profile_id FROM events.inscriptions ins " +\
        "WHERE ins.status_name != 'CANCELLED' AND tourney_id = '" + tourney_id + "' "
        
    str_where = " WHERE pm.is_active = True AND pm.id NOT IN (" + str_ins + ") "  
    
    str_search = ''
    if criteria_value:
        str_search = "AND (pm.name ilike '%" + criteria_value + "%' OR pp.level ilike '%" +\
            criteria_value + "%' OR club.name ilike '%" + criteria_value + "%' OR federations.name ilike '%" + criteria_value + "%')"
        str_where += str_search
        
    str_count += str_where
    str_query += str_where
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY pm.name DESC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_player(item, api_uri=api_uri) for item in lst_data]
    
    return result

def create_dict_row_player(item, api_uri=""):
    
    dict_row = {'profile_id': item['profile_id'], 'name': item['name'], 
               'elo': item['elo'], 'level': item['level'] if item['level'] else '', 
               'club_name': item['club_name'] if item['club_name'] else '', 
               'federation_name': item['federation_name'] if item['federation_name'] else '', 
               'photo' : get_url_avatar(item['profile_id'], item['photo'], api_uri=api_uri)}
    
    return dict_row

def get_one(invitation_id: str, db: Session):  
    return db.query(Inscriptions).filter(Inscriptions.id == invitation_id).first()

def new(request: Request, inscriptions: InscriptionsCreated, db: Session):
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_one_profile = get_one_profile(id=inscriptions.profile_id, db=db)
    if not db_one_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
   
    if db_one_profile.profile_type not in ('SINGLE_PLAYER', 'PAIR_PLAYER'):
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.profile_incorrect"))
    
    #buscar el torneo y comprobar el estado
    db_one_tourney = get_tourney_by_id(inscriptions.tourney_id, db=db)
    if not db_one_tourney:
        raise HTTPException(status_code=400, detail=_(locale, "tourney.not_found"))
   
    if db_one_tourney.status.name == 'FINALIZED':
        raise HTTPException(status_code=400, detail=_(locale, "tourney.status_incorrect"))
   
    # verificar que no se repita la inscripcion del jugador
    if verify_exist_inscription(db_one_tourney.id, inscriptions.profile_id, db=db):
        raise HTTPException(status_code=400, detail=_(locale, "inscriptions.already_exist"))
     
    one_status = get_status_by_name('CONFIRMED', db=db)
    if not one_status:
        raise HTTPException(status_code=404, detail=_(locale, "status.not_found"))
    
    db_inscription = Inscriptions(id=str(uuid.uuid4()), tourney_id=db_one_tourney.id, profile_id=inscriptions.profile_id, 
                                  user_id=None, modality=db_one_tourney.modality, was_pay=inscriptions.was_pay,
                                  payment_way=inscriptions.payment_way, import_pay=db_one_tourney.inscription_import,
                                  created_by=currentUser['username'], updated_by=currentUser['username'],
                                  created_date=datetime.today(), updated_date=datetime.today(),
                                  status_name=one_status.name)
    
    one_player = new_player_from_inscription(db_one_tourney, db_one_profile, one_status, db_inscription, db=db) 
    
    # verificar el estado de la ultima ronda del torneo.
    # Despues de Iniciada, no hago nada. En configurada o creada borrar todo y pongo la ronda en estado creada.
    
    # restar_round(one_invitation.tourney_id, db=db)
    
    try:
        db.add(db_inscription)
        db.add(one_player)
        db.commit()
        return result
       
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "event.error_new_event")               
        raise HTTPException(status_code=403, detail=msg)
    
def verify_exist_inscription(tourney_id:str, profile_id:str, db:Session):
    
    str_count = "Select count(*) FROM events.inscriptions ins " +\
        " WHERE ins.status_name != 'CANCELLED' AND tourney_id = '" + tourney_id + "' " +\
        "AND profile_id = '" + profile_id + "' "
    amount = db.execute(str_count).scalar()
    
    return True if amount != 0 else False

def update(request: Request, inscription_id: str, inscriptions: InscriptionsUpdated, db: Session):
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    # buscar la inscripcion...
    # solo se cambiara los datos del pago.
    one_inscription = get_one(inscription_id, db=db)
    if not one_inscription:
        raise HTTPException(status_code=400, detail=_(locale, "inscriptions.not_found"))
    
    #buscar el torneo y comprobar el estado
    db_one_tourney = get_tourney_by_id(one_inscription.tourney_id, db=db)
    if not db_one_tourney:
        raise HTTPException(status_code=400, detail=_(locale, "tourney.not_found"))
   
    if db_one_tourney.status.name == 'FINALIZED':
        raise HTTPException(status_code=400, detail=_(locale, "tourney.status_incorrect"))
   
    one_inscription.was_pay = inscriptions.was_pay
    if inscriptions.payment_way and inscriptions.payment_way != one_inscription.payment_way:
        one_inscription.payment_way = inscriptions.payment_way
    
    try:
        db.add(one_inscription)
        db.commit()
        result.data = {'id': one_inscription.id}
        return result
       
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "event.error_new_event")               
        raise HTTPException(status_code=403, detail=msg)