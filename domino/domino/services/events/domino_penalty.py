import math
import uuid

from datetime import datetime
from fastapi import HTTPException, Request
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from typing import List, Dict
import json
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.config.config import settings
from domino.app import _

from domino.models.events.domino_penalties import DominoBoletusPenalties

from domino.schemas.resources.result_object import ResultObject
from domino.schemas.events.domino_penalties import DominoPenaltiesCreated

from domino.services.resources.status import get_one_by_name, get_one as get_one_status
from domino.services.events.invitations import get_one_by_id as get_invitation_by_id
from domino.services.events.tourney import get_one as get_torneuy_by_eid, get_info_categories_tourney
from domino.services.events.domino_round import get_last_by_tourney, remove_configurate_round
from domino.services.events.domino_boletus import get_one as get_one_boletus
from domino.services.events.calculation_serv import get_motive_closed

from domino.services.enterprise.userprofile import get_one as get_one_profile

from domino.services.resources.utils import get_result_count, create_dir, del_image, get_ext_at_file, upfile
from domino.services.enterprise.auth import get_url_avatar

def get_penalty_by_boletus(request:Request, boletus_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 
    result.data = []
    
    str_query = "SELECT bop.id, single_profile_id, pmem.name as player_name, penalty_type, penalty_value, apply_points " +\
        "FROM events.domino_boletus_penalties bop JOIN enterprise.profile_member pmem ON pmem.id = bop.single_profile_id " +\
        "WHERE boletus_id = '" + boletus_id + "' "
    
    str_query += " ORDER BY bop.single_profile_id ASC " 
    
    lst_data_exec = db.execute(str_query)
    for item in lst_data_exec:
        result.data.append({'id': item.id, 'player_id': item.single_profile_id, 'player_name': item.player_name, 
                            'penalty_type': item.penalty_type, 'penalty_value': item.penalty_value})
    
    return result

def new(request: Request, player_id: str, domino_penalty: DominoPenaltiesCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    one_player = get_one_profile(player_id, db=db)
    if not one_player:
        raise HTTPException(status_code=404, detail=_(locale, "player.profile_not_found"))
    
    # verificar si ya tiene penalidades de ese tipo pasadas, error
    str_query = " SELECT count(id) FROM events.domino_boletus_penalties "+\
        "Where boletus_id='" + domino_penalty.boletus_id + "' and single_profile_id='" + player_id +\
        "' and penalty_type='" + domino_penalty.penalty_type + "'"
    amount_pen = db.execute(str_query).fetchone()[0]
    if amount_pen > 0:
        raise HTTPException(status_code=404, detail=_(locale, "penalty.already_exist"))
    
    one_penalty = DominoBoletusPenalties(id=str(uuid.uuid4()), boletus_id=domino_penalty.boletus_id, pair_id=None,
                                         player_id=None, single_profile_id=one_player.id, penalty_type=domino_penalty.penalty_type,
                                         penalty_amount=1, penalty_value=domino_penalty.penalty_value,
                                         apply_points=True) 
    
    try:
        db.add(one_penalty)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        return False
    
def update_one_penalty(request: Request, player_id: str, domino_penalty: DominoPenaltiesCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    one_player = get_one_profile(player_id, db=db)
    if not one_player:
        raise HTTPException(status_code=404, detail=_(locale, "player.profile_not_found"))
    
    # verificar si ya tiene penalidades de ese tipo pasadas, error
    str_query = " SELECT count(id) FROM events.domino_boletus_penalties "+\
        "Where boletus_id='" + domino_penalty.boletus_id + "' and single_profile_id='" + player_id +\
        "' and penalty_type='" + domino_penalty.penalty_type + "'"
    amount_pen = db.execute(str_query).fetchone()[0]
    if amount_pen > 0:
        raise HTTPException(status_code=404, detail=_(locale, "penalty.already_exist"))
    
    one_penalty = DominoBoletusPenalties(id=str(uuid.uuid4()), boletus_id=domino_penalty.boletus_id, pair_id=None,
                                         player_id=None, single_profile_id=one_player.id, penalty_type=domino_penalty.penalty_type,
                                         penalty_amount=1, penalty_value=domino_penalty.penalty_value,
                                         apply_points=True) 
    
    try:
        db.add(one_penalty)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        return False
    
def new_absences(request: Request, boletus_id: str, lst_players: List, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    one_boletus = get_one_boletus(boletus_id, db=db)
    if not one_boletus:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.not_found"))

    motive_closed_description=get_motive_closed('absences')
    result_close = force_closing_boletus(one_boletus, lst_players, motive_closed='absences', 
                                         motive_closed_description=motive_closed_description, db=db)
    if not result_close:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.error_force_closing"))
    
    try:
        return result
    except (Exception, SQLAlchemyError) as e:
        return False
    
def new_abandon(request: Request, boletus_id: str, lst_players: List, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    one_boletus = get_one_boletus(boletus_id, db=db)
    if not one_boletus:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.not_found"))

    motive_closed_description=get_motive_closed('abandon')
    result_close = force_closing_boletus(one_boletus, lst_players, motive_closed='abandon', 
                                         motive_closed_description=motive_closed_description, db=db)
    if not result_close:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.error_force_closing"))
    
    try:
        return result
    except (Exception, SQLAlchemyError) as e:
        return False
    
def force_closing_boletus(one_boletus, lst_players: List, motive_closed:str, motive_closed_description:str, db: Session):
    
    point_to_win = one_boletus.tourney.number_points_to_win if one_boletus.tourney.number_points_to_win else 200
    
    str_update = "UPDATE events.domino_boletus_position SET is_winner=True, positive_points=" + str(point_to_win/2) + "," +\
        "negative_points=0, penalty_points=0, expelled=False WHERE boletus_id ='" + one_boletus.id + "'"
    db.execute(str_update)
    
    str_update = "UPDATE events.domino_boletus_position SET is_winner=False, negative_points=" + str(point_to_win/2) + "," +\
        "positive_points=0, penalty_points=0, expelled=False WHERE boletus_id ='" + one_boletus.id + "' AND single_profile_id IN (" 
    str_players = ''
    for item in lst_players:
        str_players += "'" + item + "',"
    
    str_players = str_players[:-1] + ") " if str_players else ""
    if str_players:   
        str_update += str_players   
        db.execute(str_update)
    
    # marcar el boleto como que no puede ser modificado
    one_boletus.status_id = get_one_by_name('FINALIZED', db=db).id
    one_boletus.can_update = False
    one_boletus.motive_closed = motive_closed
    one_boletus.motive_closed_description = motive_closed_description
    
    try:
        db.add(one_boletus)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        return False