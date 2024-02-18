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
from domino.schemas.events.domino_penalties import DominoPenaltiesCreated, DominoAnnulledCreated, DominoAbsencesCreated

from domino.services.resources.status import get_one_by_name, get_one as get_one_status
from domino.services.events.invitations import get_one_by_id as get_invitation_by_id
from domino.services.events.tourney import get_one as get_torneuy_by_eid, get_info_categories_tourney
from domino.services.events.domino_round import get_last_by_tourney, remove_configurate_round
from domino.services.events.domino_boletus import get_one as get_one_boletus, get_info_player_of_boletus, update_info_player_pairs
from domino.services.events.calculation_serv import get_motive_closed

from domino.services.enterprise.userprofile import get_one as get_one_profile

from domino.services.resources.utils import get_result_count, create_dir, del_image, get_ext_at_file, upfile
from domino.services.enterprise.auth import get_url_avatar

def get_penalty_by_boletus(request:Request, boletus_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 

    dict_result = {'lst_data': [], 'lst_players': []}
    
    str_query = "SELECT bop.id, single_profile_id, pmem.name as player_name, penalty_type, penalty_value, apply_points " +\
        "FROM events.domino_boletus_penalties bop JOIN enterprise.profile_member pmem ON pmem.id = bop.single_profile_id " +\
        "WHERE boletus_id = '" + boletus_id + "' "
    
    str_query += " ORDER BY bop.single_profile_id ASC " 
    
    lst_data_exec = db.execute(str_query)
    for item in lst_data_exec:
        dict_result['lst_data'].append({'id': item.id, 'player_id': item.single_profile_id, 'player_name': item.player_name, 
                                        'penalty_type': item.penalty_type, 'penalty_value': item.penalty_value})
    
    dict_result['lst_players'] = get_info_player_of_boletus(boletus_id, db=db)
    result.data = dict_result
    
    return result

def new(request: Request, boletus_id: str, domino_penalty: DominoPenaltiesCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    one_boletus = get_one_boletus(boletus_id, db=db)
    if not one_boletus:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.not_found"))
    
    if one_boletus.status.name != 'INITIADED':
        raise HTTPException(status_code=404, detail=_(locale, "boletus.status_incorrect"))
    
    one_player = get_one_profile(domino_penalty.player_id, db=db)
    if not one_player:
        raise HTTPException(status_code=404, detail=_(locale, "player.profile_not_found"))
    
    penalty_type = get_type_penalty(domino_penalty.penalty_type)
    
    # verificar si ya tiene penalidades de ese tipo pasadas, error
    str_query = " SELECT count(id) FROM events.domino_boletus_penalties "+\
        "Where boletus_id='" + boletus_id + "' and single_profile_id='" + domino_penalty.player_id +\
        "' and penalty_type='" + penalty_type + "'"
    amount_pen = db.execute(str_query).fetchone()[0]
    if amount_pen > 0:
        raise HTTPException(status_code=404, detail=_(locale, "penalty.already_exist"))
    
    one_penalty = DominoBoletusPenalties(id=str(uuid.uuid4()), boletus_id=boletus_id, pair_id=None,
                                         player_id=None, single_profile_id=one_player.id, penalty_type=penalty_type,
                                         penalty_amount=1, penalty_value=domino_penalty.penalty_value,
                                         apply_points=True) 
    
    try:
        db.add(one_penalty)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        return False
   
def remove_one_penalty(request: Request, penalty_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    one_penalty = get_one_penalty(penalty_id, db=db)
    if not one_penalty:
        raise HTTPException(status_code=404, detail=_(locale, "penalty.not_found"))
    
    # si la ronda esta cerrada no se puede eliminar
    if one_penalty.boletus.status.name == 'FINALIZED':
        raise HTTPException(status_code=404, detail=_(locale, "boletus.status_incorrect"))
    
    try:
        db.delete(one_penalty)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        return False

def get_one_penalty(id: str, db: Session):  
    return db.query(DominoBoletusPenalties).filter(DominoBoletusPenalties.id == id).first()

def get_type_penalty(penalty_type):
    
    dict_penalty = {'0': 'Amonestacion', '1': 'Tarjeta Amarilla', '2': 'Tarjeta Roja'}
    return dict_penalty[penalty_type]

def get_type_annulled(annulled_type):
    
    dict_annulled = {'0': 'Sentarse Incorrectamente', '1': 'Error al Anotar', '2': 'Conducta AntiDeportiva'}
    return dict_annulled[annulled_type]
    
def new_absences(request: Request, boletus_id: str, players: DominoAbsencesCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    one_boletus = get_one_boletus(boletus_id, db=db)
    if not one_boletus:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.not_found"))

    if not one_boletus.can_update:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.can_update"))
    
    players.motive = '0' if not players.motive else players.motive
    motive_type = 'absences' if players.motive == '0' else 'abandon'
    
    motive_closed_description=get_motive_closed(motive_type)
    lst_players = players.players.split(',')
    result_close = force_closing_boletus(one_boletus, lst_players, motive_closed=motive_type, 
                                         motive_closed_description=motive_closed_description, db=db)
    if not result_close:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.error_force_closing"))
    
    try:
        return result
    except (Exception, SQLAlchemyError) as e:
        return False

def new_annulled(request: Request, boletus_id: str, domino_annulled: DominoAnnulledCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    one_boletus = get_one_boletus(boletus_id, db=db)
    if not one_boletus:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.not_found"))
    
    annulled_type = get_type_annulled(domino_annulled.annulled_type)
    one_player = None
    if domino_annulled.annulled_type == '2':  # Conducta antidepoprtiva debe traer un jugador 
        if not domino_annulled.player_id: 
            raise HTTPException(status_code=404, detail=_(locale, "penalty.player_is_requeried"))
          
        one_player = get_one_profile(domino_annulled.player_id, db=db)
        if not one_player:
            raise HTTPException(status_code=404, detail=_(locale, "player.profile_not_found"))
    
    # quitar los puntos a todos los jugadores y calcular las estadísticas de ellos
    # si fue explusado, cambiar el estado del jugador
    
    force_annulled_boletus(one_boletus, domino_annulled.annulled_type, annulled_type, db=db, player_id=one_player.id if one_player else None)
    
    one_boletus.is_valid = False
    
    try:
        db.add(one_boletus)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        return False

def get_all_reason_no_update(request:Request, boletus_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    result = ResultObject() 
    
    one_boletus = get_one_boletus(boletus_id, db=db)
    if not one_boletus:
        raise HTTPException(status_code=404, detail=_(locale, "boletus.not_found"))
    
    dict_result = {'motive_closed': one_boletus.motive_closed, 'motive_closed_description': one_boletus.motive_closed_description,
                   'is_valid': one_boletus.is_valid, 'motive_not_valid': one_boletus.motive_not_valid, 
                   'motive_not_valid_description': one_boletus.motive_not_valid_description, 'lst_player': []}

    str_query = "Select single_profile_id, position_id, pmem.name as player_name from events.domino_boletus_position bop " +\
        "JOIN enterprise.profile_member pmem ON pmem.id = bop.single_profile_id " +\
        "where boletus_id = '" + boletus_id + "' and is_guilty_closure=True "
    lst_data_exec = db.execute(str_query)
    for item in lst_data_exec:
        dict_result['lst_player'].append(
            {'position_id': item.position_id, 'player_id': item.single_profile_id, 'player_name': item.player_name})
    
    result.data = dict_result
    return result

def force_closing_boletus(one_boletus, lst_players: List, motive_closed:str, motive_closed_description:str, db: Session):
    
    point_to_win = one_boletus.tourney.points_for_absences if one_boletus.tourney.points_for_absences else 200
    
    str_update = "UPDATE events.domino_boletus_position SET is_winner=True, positive_points=" + str(point_to_win) + "," +\
        "negative_points=0, penalty_points=0, expelled=False WHERE boletus_id ='" + one_boletus.id + "'"
    db.execute(str_update)
    
    str_update = "UPDATE events.domino_boletus_position SET is_winner=False, negative_points=" + str(point_to_win) + "," +\
        "positive_points=0, penalty_points=0, expelled=False, is_guilty_closure=True " +\
        "WHERE boletus_id ='" + one_boletus.id + "' AND single_profile_id IN (" 
    str_players = ''
    for item in lst_players:
        str_players += "'" + item + "',"
    
    str_players = str_players[:-1] + ") " if str_players else ""
    if str_players:   
        str_update += str_players   
        db.execute(str_update)
    
    str_query = "SELECT pairs_id, SUM(positive_points)/2 positive_points, SUM(negative_points)/2 negative_points " +\
        "FROM events.domino_boletus_position WHERE boletus_id ='" + one_boletus.id + "' group by pairs_id "
    
    lst_pair = db.execute(str_query)
    str_pair_update = ''
    one_points, two_points = 0, 0 
    one_pair, two_pair = '', ''
    for item in lst_pair:
        str_pair_update += "UPDATE events.domino_boletus_pairs SET positive_points = " + str(item.positive_points) +\
            ", negative_points = " + str(item.negative_points) + " WHERE pairs_id = '" + item.pairs_id + \
            "' and boletus_id ='" + one_boletus.id + "';  "
        if not one_points:
            one_points = item.positive_points
            one_pair = item.pairs_id
        else:
            two_points = item.positive_points
            two_pair = item.pairs_id
            
    db.execute(str_pair_update) 
    str_pair_winner = ""
    if one_points ==  two_points :  #empatados, no gana nadie  
        str_pair_winner = "UPDATE events.domino_boletus_pairs SET is_winner = False " +\
            " WHERE boletus_id ='" + one_boletus.id + "';"
    else:
        if one_points > two_points:
            str_pair_winner = "UPDATE events.domino_boletus_pairs SET is_winner = True " +\
                " WHERE boletus_id ='" + one_boletus.id + "' AND pairs_id = '" + one_pair + "';"
        else:
            str_pair_winner = "UPDATE events.domino_boletus_pairs SET is_winner = True " +\
                " WHERE boletus_id ='" + one_boletus.id + "' AND pairs_id = '" + two_pair + "';"
                
    if str_pair_winner:  
        db.execute(str_pair_winner) 
          
    # marcar el boleto como que no puede ser modificado
    one_boletus.status_id = get_one_by_name('FINALIZED', db=db).id
    one_boletus.can_update = False
    one_boletus.motive_closed = motive_closed
    one_boletus.motive_closed_description = motive_closed_description
    
    try:
        db.add(one_boletus)
        db.commit()
        
        update_info_player_pairs(one_boletus, db=db)
        
        return True
    except (Exception, SQLAlchemyError) as e:
        return False
    
def force_annulled_boletus(one_boletus, motive_not_valid: str, motive_not_valid_description:str, db: Session, player_id:str=None, expelled=False):
    
    if not player_id: # todo el mundo pierde
        str_update = "UPDATE events.domino_boletus_position SET is_winner=False, positive_points=0, " +\
            "negative_points=0, penalty_points=0, expelled=False, is_guilty_closure=True WHERE boletus_id ='" + one_boletus.id + "';"
        str_update += "UPDATE events.domino_boletus_pairs SET positive_points = 0, negative_points = 0" +\
            " WHERE boletus_id ='" + one_boletus.id + "';  "
        db.execute(str_update)
    else:
        point_to_win = one_boletus.tourney.points_for_absences if one_boletus.tourney.points_for_absences else 200
        
        str_update = "UPDATE events.domino_boletus_position SET is_winner=True, positive_points=" + str(point_to_win) + "," +\
            "negative_points=0, penalty_points=0, expelled=False WHERE boletus_id ='" + one_boletus.id + "';"
        str_update += "UPDATE events.domino_boletus_position SET is_winner=False, is_guilty_closure=True, positive_points=0, " +\
            "negative_points=" + str(point_to_win) + ", expelled=" + str(expelled) +\
            " WHERE boletus_id ='" + one_boletus.id + "' AND single_profile_id = '" + player_id + "'; "
        if expelled:
            status_exp_id = get_one_by_name('EXPELLED', db=db).id
            
            str_update += "UPDATE events.players pa SET status_id = " + str(status_exp_id) +\
                " WHERE id IN (Select pu.player_id from events.players_users pu " +\
                "join events.players pa ON pa.id = pu.player_id where pu.profile_id = '" + player_id + "' " +\
                " and pa.tourney_id = '" + one_boletus.tourney.id + "'); "
        db.execute(str_update)
    
        str_query = "SELECT pairs_id, SUM(positive_points)/2 positive_points, SUM(negative_points)/2 negative_points " +\
            "FROM events.domino_boletus_position WHERE boletus_id ='" + one_boletus.id + "' group by pairs_id "
        
        lst_pair = db.execute(str_query)
        str_pair_update = ''
        one_points, two_points = 0, 0 
        one_pair, two_pair = '', ''
        for item in lst_pair:
            str_pair_update += "UPDATE events.domino_boletus_pairs SET positive_points = " + str(item.positive_points) +\
                ", negative_points = " + str(item.negative_points) + " WHERE pairs_id = '" + item.pairs_id + \
                "' and boletus_id ='" + one_boletus.id + "';  "
            if not one_points:
                one_points = item.positive_points
                one_pair = item.pairs_id
            else:
                two_points = item.positive_points
                two_pair = item.pairs_id
                
        db.execute(str_pair_update) 
        str_pair_winner = ""
        if one_points ==  two_points :  #empatados, no gana nadie  
            str_pair_winner = "UPDATE events.domino_boletus_pairs SET is_winner = False " +\
                " WHERE boletus_id ='" + one_boletus.id + "';"
        else:
            if one_points > two_points:
                str_pair_winner = "UPDATE events.domino_boletus_pairs SET is_winner = True " +\
                    " WHERE boletus_id ='" + one_boletus.id + "' AND pairs_id = '" + one_pair + "';"
            else:
                str_pair_winner = "UPDATE events.domino_boletus_pairs SET is_winner = True " +\
                    " WHERE boletus_id ='" + one_boletus.id + "' AND pairs_id = '" + two_pair + "';"
                    
        if str_pair_winner:  
            db.execute(str_pair_winner)
                
    # marcar el boleto como que no puede ser modificado
    one_boletus.status_id = get_one_by_name('FINALIZED', db=db).id
    one_boletus.can_update = False
    one_boletus.motive_closed = 'annulled'
    one_boletus.motive_closed_description = get_motive_closed('annulled')
    
    one_boletus.motive_not_valid = motive_not_valid
    one_boletus.motive_not_valid_description = motive_not_valid_description
    
    try:
        db.add(one_boletus)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        return False