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

from domino.models.events.domino_boletus import DominoBoletus, DominoBoletusPosition, DominoBoletusPairs

from domino.schemas.resources.result_object import ResultObject

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.events.domino_table import get_lst_tables
   
def get_one(boletus_id: str, db: Session):  
    return db.query(DominoBoletus).filter(DominoBoletus.id == boletus_id).first()

def get_one_boletus_pair(boletus_id: str, pair_id: str, db: Session):  
    return db.query(DominoBoletusPairs).filter(DominoBoletusPairs.boletus_id == boletus_id).\
        filter(DominoBoletusPairs.pairs_id == pair_id).first()

def get_all_by_round(round_id: str, db: Session):  
    return db.query(DominoBoletus).filter(DominoBoletus.round_id == round_id).all()

def get_one_by_id(round_id: str, db: Session): 
    result = ResultObject()  
    
    one_boletus = get_one(round_id, db=db)
    if not one_boletus:
        raise HTTPException(status_code=404, detail="boletus.not_found")
    
    str_query = "SELECT dtab.id, dtab.tourney_id, table_number, is_smart, amount_bonus, dtab.image, dtab.is_active, tourney.name " +\
        "FROM events.domino_tables dtab " + \
        "Join events.tourney ON tourney.id = dtab.tourney_id " +\
        " WHERE dtab.id = '" + str(round_id) + "' "  
    lst_data = db.execute(str_query) 
    
    for item in lst_data: 
        result.data = [create_dict_row(item, one_boletus.tourney_id, 0, db=db) for item in lst_data]
        
    if not result.data:
        raise HTTPException(status_code=404, detail="round.not_found")
    
    return result

def create_dict_row(item, tourney_id, page, db: Session, api_uri=""):
    
    image_name = item['image'] if item['image'] else item['image_tourney']
    image = api_uri + "/api/public/advertising/" + str(item['tourney_id']) + "/" + image_name
    
    new_row = {'id': item['id'], 'table_number': item['table_number'], 
               'is_smart': item['is_smart'], 'amount_bonus': item['amount_bonus'], 
               'tourney_name': item['name'], 'is_active': item['is_active'],
               'photo' : image, 'filetables':[]}
    if page != 0:
        new_row['selected'] = False
        
    if item['is_smart']:
        str_files = "Select id, position, is_ready from events.files_tables Where table_id = '" + item['id'] + "' "
        lst_files = db.execute(str_files)
        for item_f in lst_files:
            new_row['filetables'].append({'file_id': item_f.id, 'position': item_f.position, 'is_ready': item_f.is_ready})
    
    return new_row

# def created_boletus_for_round_richard(db_tourney, db_round, db:Session):

#     # obtener listado de mesas del torneo
#     lst_tables = get_lst_tables(db_tourney.id, db=db)
#     if not lst_tables:
#         raise HTTPException(status_code=404, detail="dominotables.not_exists")
        
#     # obtener listado de parejas
#     lst_players = get_lst_players_with_profile(db_tourney.id, db_round.id, db=db)
    
#     # asociar a cada mesa los 4 jugadores que le tocarian.
#     lst_dist_tables = []
#     amount_tables = len(lst_tables)
#     for i in range(amount_tables):
#         i+=1
#         j=i*4-4
#         table_id = lst_tables[i-1].id
#         dict_tables = {'table_id': table_id, 'table_number': lst_tables[i-1].table_number, 'lst_player': []}
#         for j in range(j,i*4):
#             if j > len(lst_players)-1:
#                 break
#             dict_tables['lst_player'].append(lst_players[j])
#         lst_dist_tables.append(dict_tables)

#     dict_position_table = {1:1, 2:3, 3:2, 4:4}
    
#     # Por cada mesa, ubicar los jugadores
#     for item_tab in lst_dist_tables:
#         # crear la boleta a sociada a cada jugador. En el individual debo ver si se crea boleta para cada jugador o es similar a la pareja
#         # despues si no es una boleta por cada jugador tengo que cambiar esto.
        
#         position_id = 1
#         for item_player in item_tab['lst_player']:
            
#             one_boletus = DominoBoletus(tourney_id=db_tourney.id, round_id=db_round.id, table_id=item_tab['table_id'],
#                                         player_id=item_player['player_id'], is_valid=True, is_winner=False)
#             one_position = DominoBoletusPosition(position_id=dict_position_table[position_id], 
#                                                  single_profile_id=item_player['single_profile_id'])
#             position_id+=1
            
#             one_boletus.boletus_position.append((one_position))
#             db.add(one_boletus)
        
#     db.commit()    
    
#     return True       

def created_boletus_position(one_boletus, lst_player:list, db:Session, can_update=True, points_to_win=200):
    
    positive_points = points_to_win/2 if not can_update else 0
    negative_points = 0
    is_winner = True if not can_update else False
    
    one_bol_position=DominoBoletusPosition(
            boletus_id=one_boletus.id, position_id=1, single_profile_id=lst_player[0]['one_player_id'] if lst_player[0]['one_player_id'] else None,
            scale_number=lst_player[0]['scale_number_one_player'] if lst_player[0]['scale_number_one_player'] else None,
            positive_points=positive_points, negative_points=negative_points, is_winner=is_winner, penalty_points=0,
            pairs_id=lst_player[0]['id'])
    one_boletus.boletus_position.append((one_bol_position))
    one_bol_position=DominoBoletusPosition(
            boletus_id=one_boletus.id, position_id=3, single_profile_id=lst_player[0]['two_player_id'] if lst_player[0]['two_player_id'] else None,
            scale_number=lst_player[0]['scale_number_two_player'] if lst_player[0]['scale_number_two_player'] else None,
            positive_points=positive_points, negative_points=negative_points, is_winner=is_winner, penalty_points=0,
            pairs_id=lst_player[0]['id'])
    one_boletus.boletus_position.append((one_bol_position))
        
    if len(lst_player) == 2:  #tengo las dos parejas por mesa
        one_bol_position=DominoBoletusPosition(
            boletus_id=one_boletus.id, position_id=2, single_profile_id=lst_player[1]['one_player_id'] if lst_player[1]['one_player_id'] else None,
            scale_number=lst_player[1]['scale_number_one_player'] if lst_player[1]['scale_number_one_player'] else None,
            positive_points=positive_points, negative_points=negative_points, is_winner=is_winner, penalty_points=0,
            pairs_id=lst_player[1]['id'])
        one_boletus.boletus_position.append((one_bol_position))
        one_bol_position=DominoBoletusPosition(
            boletus_id=one_boletus.id, position_id=4, single_profile_id=lst_player[1]['two_player_id'] if lst_player[0]['two_player_id'] else None,
            scale_number=lst_player[1]['scale_number_two_player'] if lst_player[1]['scale_number_two_player'] else None,
            positive_points=positive_points, negative_points=negative_points, is_winner=is_winner, penalty_points=0,
            pairs_id=lst_player[1]['id'])
        one_boletus.boletus_position.append((one_bol_position))
            
    return True

def created_boletus_for_round(tourney_id, round_id, db:Session, points_to_win=200):

    # obtener listado de mesas del torneo
    lst_tables = get_lst_tables(tourney_id, db=db)
    if not lst_tables:
        raise HTTPException(status_code=404, detail="tables.not_found")
    
    # obtener escalafon de parejas.
    lst_pairs = get_list_rounds_pairs(round_id, db=db)
    
    # asociar a cada mesa los 2 parejas que le tocarian.
    lst_dist_tables = []
    amount_tables = len(lst_tables)
    str_player = ''
    for i in range(amount_tables):
        i+=1
        j=i*2-2
        table_id = lst_tables[i-1].id
        dict_tables = {'table_id': table_id, 'table_number': lst_tables[i-1].table_number, 'lst_player': []}
        for j in range(j,i*2):
            if j > len(lst_pairs)-1:
                break
            dict_tables['lst_player'].append(lst_pairs[j])
            str_player += ' ' + lst_pairs[j]['id']
        lst_dist_tables.append(dict_tables)

    one_status_init = get_one_status_by_name('INITIADED', db=db)
    one_status_end = get_one_status_by_name('FINALIZED', db=db)
    
    # Por cada mesa, ubicar los jugadores
    for item_tab in lst_dist_tables:
        boletus_id = str(uuid.uuid4())
        one_boletus = DominoBoletus(id=boletus_id, tourney_id=tourney_id, round_id=round_id, table_id=item_tab['table_id'],
                                    is_valid=True, can_update=True)
        one_boletus.status_id = one_status_init.id
        
        if item_tab['lst_player']:
            boletus_pair_one = DominoBoletusPairs(boletus_id=boletus_id, pairs_id=item_tab['lst_player'][0]['id'], is_initiator=True)
            one_boletus.boletus_pairs.append(boletus_pair_one)
            can_update = True
            if len(item_tab['lst_player']) == 2:  #tengo las dos parejas por mesa
                boletus_pair_two = DominoBoletusPairs(boletus_id=boletus_id, pairs_id=item_tab['lst_player'][1]['id'],
                                                      is_initiator=False)
                one_boletus.boletus_pairs.append(boletus_pair_two)
            else:
                can_update = False
                
            created_boletus_position(one_boletus, lst_player=item_tab['lst_player'], db=db, can_update=can_update, points_to_win=points_to_win)
        
        if not can_update:   
            one_boletus.status_id = one_status_end.id
            one_boletus.can_update = False
            one_boletus.motive_closed = 'non_completion'
            one_boletus.motive_closed_description = 'Cerrado por no completamiento de mesa'        
        db.add(one_boletus) 
    
    # ESTO YA NO SE CUMPLE- TODOS SE SIENTAN    
    # los jugadores que no posiciono, ponerlso en estado de espera
    # one_status_wait = get_one_status_by_name('INITIADED', db=db)
    
    # str_update_play = "UPDATE events.players SET status_id = " + str(one_status_wait.id) +\
    #     " WHERE id IN ("
    # str_update_id = ""    
    # for item in lst_pairs:
    #     if item['id'] not in str_player:
    #         str_update_id += "'" + item['id'] + "',"

    # if str_update_id:
    #     str_update_id = str_update_id[:-1] + ");COMMIT;"
    
    #     str_update_play += str_update_id       
    
    db.commit()    
    
    return True      

def get_list_rounds_pairs(round_id,  db: Session):
    
    str_query = "SELECT id, one_player_id, two_player_id, name as pair_name, " +\
        "scale_number_one_player, scale_number_two_player " +\
        "FROM events.domino_rounds_pairs Where round_id = '" + round_id + "' ORDER BY position_number ASC "
    
    lst_all_pair = db.execute(str_query)
    lst_pairs = []
    for item in lst_all_pair:
        lst_pairs.append({'id': item.id, 'one_player_id': item.one_player_id, 
                          'two_player_id': item.two_player_id, 'pair_name': item.pair_name,
                          'scale_number_one_player': item.scale_number_one_player,
                          'scale_number_two_player': item.scale_number_two_player})
    
    return lst_pairs

def get_info_player_of_boletus(boletus_id: str, db: Session):
    
    lst_data = []
    
    str_query = "SELECT single_profile_id, pmem.name, position_id FROM events.domino_boletus_position bpo " +\
        "join enterprise.profile_member pmem ON pmem.id = bpo.single_profile_id " +\
        "where boletus_id = '" + boletus_id + "' order by position_id "
        
    lst_data_exec = db.execute(str_query)
    for item in lst_data_exec:
        lst_data.append({'profile_id':  item.single_profile_id, 'profile_name': item.name, 'position_id': item.position_id})
    
    return lst_data

def calculate_amount_tables_playing(round_id: str, db: Session):
    
    str_query = "Select count(*) from events.domino_boletus bol " +\
        "join resources.entities_status sta ON sta.id = bol.status_id " +\
        "where sta.name = 'INITIADED' and round_id = '" + round_id + "' " 
    amount_play = db.execute(str_query).fetchone()[0]
    return int(amount_play)

def calculat_at_close_boletus(one_boletus, db: Session, verify_point_for_time=False):
    
    dict_result = {'result': True, 'msg': ''}
    
    str_query = "Select win_pair_id, SUM(number_points) number_points from events.domino_boletus_data " +\
        "Where boletus_id = '" + one_boletus.id + "' Group by win_pair_id " 
    lst_pairs = db.execute(str_query)
    
    id_one_pair, id_two_pair = "", ""
    for item_pa in one_boletus.boletus_pairs:
        if not id_one_pair:
            id_one_pair = item_pa.pairs_id
        else:
            id_two_pair = item_pa.pairs_id
            
    points_one_pair, points_two_pair = 0, 0
    for item in lst_pairs:
        if item.win_pair_id == id_one_pair:
            points_one_pair += item.number_points
        else:
            points_two_pair += item.number_points
    
    if verify_point_for_time:
        
        if not points_one_pair and not points_two_pair:
            dict_result['result'] = False
            dict_result['msg']="boletus.equal_positive_points"
            
        if points_one_pair == points_two_pair: # estan empatados, no se puede cerrar
            dict_result['result'] = False
            dict_result['msg']="boletus.equal_positive_points"
            
        if not dict_result['result']:
            return dict_result
        
    if points_one_pair > points_two_pair:
        positive_points, negative_points = points_one_pair, points_two_pair
        win_pair_id, lost_pair_id = id_one_pair, id_two_pair
    else:
        positive_points, negative_points = points_two_pair, points_one_pair
        win_pair_id, lost_pair_id = id_two_pair, id_one_pair
    
    #incluir las penalidades
    str_query = "Select single_profile_id, SUM(penalty_value) penalty_value FROM events.domino_boletus_penalties bpe " +\
        "Where boletus_id = '" + one_boletus.id + "' group by single_profile_id " 
    lst_penalty = db.execute(str_query)
    dict_penalty = {}
    for item_pe in lst_penalty:
        dict_penalty[item_pe.single_profile_id] = int(item_pe.penalty_value)
    str_update_pen = ""
    for item_key, item_value in dict_penalty.items():
        str_update_pen += "UPDATE events.domino_boletus_position SET penalty_points = " + str(int(item_value)) +\
            " WHERE boletus_id = '" + one_boletus.id + "' AND single_profile_id = '" + str(item_key) + "';" 
    if str_update_pen:
        str_update_pen += " COMMIT; "
        db.execute(str_update_pen)
            
    # sumar el acumulado de penalidades por parejas
    str_pen= "SELECT pairs_id, SUM(penalty_points) penalty_points FROM events.domino_boletus_position " +\
        "Where boletus_id = '" + one_boletus.id + "' Group by pairs_id "
    lst_sum_pen = db.execute(str_pen)
    penalty_point_win, penalty_point_lost = 0, 0
    for item in lst_sum_pen:
        if item.pairs_id == win_pair_id:  
            penalty_point_win += int(item.penalty_points)
        else: 
            penalty_point_lost += int(item.penalty_points) 
    
    str_fields_win = "is_winner=True, penalty_points= " + str(penalty_point_win) + ", positive_points = " + str(positive_points) +\
        ", negative_points=" + str(negative_points)
    str_fields_win += " WHERE pairs_id = '" + win_pair_id + "'; "
    str_update_bol_win = "UPDATE events.domino_boletus_position SET " + str_fields_win 
    str_update_win = "UPDATE events.domino_boletus_pairs SET " + str_fields_win + str_update_bol_win
    
    str_fields_lost = "is_winner=False, penalty_points= " + str(penalty_point_lost) + ", positive_points = " + str(negative_points) + ", negative_points=" + str(positive_points)
    str_fields_lost += " WHERE pairs_id = '" + lost_pair_id + "'; "
    str_update_bol_lost = "UPDATE events.domino_boletus_position SET " + str_fields_lost 
    str_update_lost = "UPDATE events.domino_boletus_pairs SET " + str_fields_lost + str_update_bol_lost + "COMMIT;"
    
    str_update = str_update_win + str_update_lost
    db.execute(str_update)
    
    # actualizar tabla de ronda pareja
    str_round_pair = "Select pairs_id, is_winner, positive_points, negative_points, penalty_points " +\
        "from events.domino_boletus_pairs where boletus_id = '" + one_boletus.id + "' "
    lst_pairs = db.execute(str_round_pair)
    
    str_update_round_pa = ""
    for item_pa in lst_pairs:
        
        games_won = 1 if item_pa.is_winner else 0
        games_lost = 1 if not item_pa.is_winner else 0
        points_positive = item_pa.positive_points
        points_negative = item_pa.negative_points
        penalty_points = item_pa.penalty_points
        points_difference = item_pa.positive_points - item_pa.negative_points - item_pa.penalty_points

        str_update_round_pa += "UPDATE events.domino_rounds_pairs SET games_won = " + str(games_won) +\
            ", games_lost = " + str(games_lost) + ", points_positive = " + str(points_positive) +\
            ", points_negative= " + str(points_negative) + ", penalty_points = " + str(penalty_points) +\
            ", points_difference = " + str(points_difference) + " WHERE id = '" + item_pa.pairs_id + "'; "
    if str_update_round_pa:
        str_update_round_pa += "COMMIT;"
        db.execute(str_update_round_pa) 
    
    print(str_update_round_pa)   
    print('********') 
    # actualizar tabla de scale de cada player
    
    
    try:
        
        db.commit() 
        
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        dict_result['result'] = False
        dict_result['msg']="boletus.error_writing"
    
    return dict_result

# def created_boletus_for_round_ubica_no_consecutivo_sino_saltanto(tourney_id, round_id, db:Session):

#     # obtener listado de mesas del torneo
#     lst_tables = get_lst_tables(tourney_id, db=db)
#     if not lst_tables:
#         raise HTTPException(status_code=404, detail="dominotables.not_exists")
    
#     # obtener escalafon de parejas.
#     lst_pairs = get_list_rounds_pairs(round_id, db=db)
    
#     lst_par, lst_impar, pos = [], [], 0
#     for i in lst_pairs:   
#         if  pos % 2 == 0:
#             lst_par.append(lst_pairs[pos])
#         else:
#             lst_impar.append(lst_pairs[pos])
#         pos+=1 
    
#     # asociar a cada mesa los 2 parejas que le tocarian.
#     lst_dist_tables = []
#     amount_tables = len(lst_tables)
    
#     for i in range(amount_tables-1):
#         dict_tables = {'table_id': lst_tables[i].id, 'table_number': lst_tables[i].table_number, 'lst_player': []}
#         if  i % 2 == 0:
#             dict_tables['lst_player'].append(lst_par[i])
#             dict_tables['lst_player'].append(lst_par[i+1])
            
#         else: 
#             dict_tables['lst_player'].append(lst_impar[i-1])
#             dict_tables['lst_player'].append(lst_impar[i])
        
#         lst_dist_tables.append(dict_tables)

#     # Por cada mesa, ubicar los jugadores
#     for item_tab in lst_dist_tables:
#         boletus_id = str(uuid.uuid4())
#         one_boletus = DominoBoletus(id=boletus_id, tourney_id=tourney_id, round_id=round_id, table_id=item_tab['table_id'],
#                                     is_valid=True)
        
#         one_data = DominoBoletusData(id=str(uuid.uuid4()), boletus_id=boletus_id, data_number=1)
#         one_boletus.boletus_data.append(one_data)
    
#         if item_tab['lst_player']:
#             boletus_pair_one = DominoBoletusPairs(boletus_id=boletus_id, pairs_id=item_tab['lst_player'][0]['id'], is_initiator=True)
#             one_boletus.boletus_pairs.append(boletus_pair_one)
#             if len(item_tab['lst_player']) == 2:  #tengo las dos parejas por mesa
#                 boletus_pair_two = DominoBoletusPairs(boletus_id=boletus_id, pairs_id=item_tab['lst_player'][1]['id'],
#                                                       is_initiator=False)
#                 one_boletus.boletus_pairs.append(boletus_pair_two)
                
#             created_boletus_position(one_boletus, lst_player=item_tab['lst_player'], db=db)
                    
#         db.add(one_boletus)        
    
#     db.commit()    
    
#     return True     
