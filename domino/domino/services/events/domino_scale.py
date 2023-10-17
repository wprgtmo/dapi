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
from fastapi.responses import FileResponse
from os import getcwd

from domino.models.events.domino_scale import DominoScale


from domino.schemas.events.domino_rounds import DominoScaleCreated
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
from domino.services.enterprise.userprofile import get_one as get_one_profile
from domino.services.enterprise.auth import get_url_avatar

from domino.services.events.tourney import get_one as get_one_tourney, get_setting_tourney

def new_initial_round(request: Request, tourney_id:str, dominoscale: list[DominoScaleCreated], db: Session):
# def new_initial_round(request: Request, tourney_id:str, dominoscale: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_tourney = get_one_tourney(tourney_id, db=db)
    if not db_tourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.not_found"))
    
    one_status_init = get_one_status_by_name('INITIADED', db=db)
    
    # if db_tourney.status_id != one_status_init.id:
    #     raise HTTPException(status_code=404, detail=_(locale, "tourney.tourney_closed"))
    
    one_settingtourney = get_setting_tourney(db_tourney.id, db=db)
    if not one_settingtourney:
        raise HTTPException(status_code=404, detail=_(locale, "tourney.setting_tourney_not_exist"))
    
    # si el torneo ya tiene mas de una ronda no se puede hacer esto
    str_query = "Select count(*) FROM events.domino_rounds WHERE tourney_id = '" + tourney_id + "' "
    amount_round = db.execute(str_query).fetchone()[0]
    
    if amount_round != 1:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_initial_round"))
    
    str_query = "Select id FROM events.domino_rounds WHERE tourney_id = '" + tourney_id + "' and round_number = 1 "
   
    round_id = db.execute(str_query).fetchone()
    if not round_id:
        raise HTTPException(status_code=404, detail=_(locale, "round.not_initial_round"))
    
    round_id = round_id[0]
    
    if one_settingtourney.lottery_type == 'MANUAL':
        initial_scale_by_manual_lottery(tourney_id, round_id, dominoscale, db=db)
    else:
        initial_scale_by_automatic_lottery(dominoscale, db=db)
    
    # distribuir por mesas
    
    return result
  
def initial_scale_by_manual_lottery(tourney_id: str, round_id: str, dominoscale:str, db: Session):
    
    for item in dominoscale:
        one_scale = DominoScale(id=str(uuid.uuid4()), tourney_id=tourney_id, round_id=round_id, round_number=1, 
                                position_number=int(item.number), player_id=item.id, is_active=True)
        db.add(one_scale)
        
    db.commit()
    
    return True

def initial_scale_by_automatic_lottery(dominoscale:str, db: Session):
    
    lst_dominoscale = dominoscale.split(';')
    for item in lst_dominoscale:
        info_position = item.split(',')
        print(info_position[0])
        print(info_position[1])
        print('***************')
    
    return True

def get_lst_players(tourney_id: str, round_id: str, db: Session):  
    return db.query(DominoScale).filter(DominoScale.tourney_id == tourney_id).\
        filter(DominoScale.round_id == round_id).order_by(DominoScale.position_number).all()
        
def get_lst_players_with_profile(tourney_id: str, round_id: str, db: Session):  
    
    lst_player = []
    
    str_query = "Select doms.player_id, puser.single_profile_id From events.domino_scale doms " +\
        "join events.players play ON play.id = doms.player_id " +\
        "join enterprise.profile_users puser ON puser.profile_id = play.profile_id " +\
        "Where doms.tourney_id = '" + tourney_id + "' and round_id = '" + round_id + "' "
    lst_result = db.execute(str_query)
    for item in lst_result:
        lst_player.append({'player_id': item.player_id, 'single_profile_id': item.single_profile_id})
    
    return lst_player
        
def get_all_players_by_tables(request:Request, page: int, per_page: int, tourney_id: str, round_id: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
            
    str_from = "FROM events.domino_boletus_position bpos " +\
        "JOIN events.domino_boletus bol ON bol.id = bpos.boletus_id " +\
        "JOIN events.domino_tables dtab ON dtab.id = bol.table_id " +\
        "JOIN events.setting_tourney stou ON stou.tourney_id = bol.tourney_id " +\
        "JOIN enterprise.profile_single_player psin ON psin.profile_id = bpos.single_profile_id " +\
        "JOIN enterprise.profile_member pro ON pro.id = psin.profile_id " +\
        "left join resources.city ON city.id = pro.city_id " + \
        "left join resources.country ON country.id = city.country_id "
    
    str_count = "Select count(*) " + str_from
    str_query = "SELECT bpos.position_id, bpos.single_profile_id, bol.is_winner, dtab.id as table_id, " +\
        "dtab.table_number, is_smart, amount_bonus, dtab.image as table_image, psin.elo, psin.ranking, psin.level, " +\
        "city.name as city_name, country.name as country_name, stou.image as tourney_image, pro.photo " + str_from

    str_where = "WHERE bol.is_valid is True AND dtab.is_active is True " + \
        " AND  bol.tourney_id = '" + tourney_id + "' AND bol.round_id = '" + round_id + "' "
    
    str_count += str_where
    str_query += str_where

    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY dtab.table_number, bpos.position_id " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item, tourney_id, page, db=db, api_uri=api_uri) for item in lst_data]
    
    return result

def create_dict_row(item, tourney_id, page, db: Session, api_uri):
    
    photo = get_url_avatar(item['single_profile_id'], item['photo'], api_uri=api_uri)
    table_image = item['table_image'] if item['table_image'] else item['tourney_image'] # mesa tiene imagen asociada
        
    
    new_row = {'position_id': item['position_id'], 'table_id': item['table_id'], 
               'table_number': item['table_number'], 'is_smart': item['is_smart'],  
               'amount_bonus': item['amount_bonus'], 'table_image': table_image,  
               'country': item['country_name'], 'city_name': item['city_name'],  
               'photo' : photo, 'elo': item['elo'], 'ranking': item['ranking'], 'level': item['level']}
    
    if page != 0:
        new_row['selected'] = False
    
    return new_row