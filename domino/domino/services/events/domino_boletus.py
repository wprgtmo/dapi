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
from domino.models.events.domino_data import DominoBoletusData
from domino.models.events.tourney import SettingTourney

from domino.schemas.events.events import EventBase, EventSchema
from domino.schemas.resources.result_object import ResultObject

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
from domino.services.enterprise.users import get_one_by_username
from domino.services.enterprise.userprofile import get_one as get_one_profile
from domino.services.events.domino_table import get_lst_tables
   
def get_one(boletus_id: str, db: Session):  
    return db.query(DominoBoletus).filter(DominoBoletus.id == boletus_id).first()

def get_one_by_id(round_id: str, db: Session): 
    result = ResultObject()  
    
    one_boletus = get_one(round_id, db=db)
    if not one_boletus:
        raise HTTPException(status_code=404, detail="dominoboletus.not_found")
    
    str_query = "SELECT dtab.id, dtab.tourney_id, table_number, is_smart, amount_bonus, dtab.image, dtab.is_active, tourney.name " +\
        "FROM events.domino_tables dtab " + \
        "Join events.tourney ON tourney.id = dtab.tourney_id " +\
        " WHERE dtab.id = '" + str(round_id) + "' "  
    lst_data = db.execute(str_query) 
    
    for item in lst_data: 
        result.data = [create_dict_row(item, one_boletus.tourney_id, 0, db=db) for item in lst_data]
        
    if not result.data:
        raise HTTPException(status_code=404, detail="dominoround.not_found")
    
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

def created_boletus_position(one_boletus, lst_player:list, db:Session):
    
    one_bol_position=DominoBoletusPosition(
            boletus_id=one_boletus.id, position_id=1, single_profile_id=lst_player[0]['one_player_id'] if lst_player[0]['one_player_id'] else None,
            scale_number=lst_player[0]['scale_number_one_player'] if lst_player[0]['scale_number_one_player'] else None)
    one_boletus.boletus_position.append((one_bol_position))
    one_bol_position=DominoBoletusPosition(
            boletus_id=one_boletus.id, position_id=3, single_profile_id=lst_player[0]['two_player_id'] if lst_player[0]['two_player_id'] else None,
            scale_number=lst_player[0]['scale_number_two_player'] if lst_player[0]['scale_number_two_player'] else None)
    one_boletus.boletus_position.append((one_bol_position))
        
    if len(lst_player) == 2:  #tengo las dos parejas por mesa
        one_bol_position=DominoBoletusPosition(
            boletus_id=one_boletus.id, position_id=2, single_profile_id=lst_player[1]['one_player_id'] if lst_player[1]['one_player_id'] else None,
            scale_number=lst_player[1]['scale_number_one_player'] if lst_player[1]['scale_number_one_player'] else None)
        one_boletus.boletus_position.append((one_bol_position))
        one_bol_position=DominoBoletusPosition(
            boletus_id=one_boletus.id, position_id=4, single_profile_id=lst_player[1]['two_player_id'] if lst_player[0]['two_player_id'] else None,
            scale_number=lst_player[1]['scale_number_two_player'] if lst_player[1]['scale_number_two_player'] else None)
        one_boletus.boletus_position.append((one_bol_position))
            
    return True

def created_boletus_for_round(tourney_id, round_id, db:Session):

    # obtener listado de mesas del torneo
    lst_tables = get_lst_tables(tourney_id, db=db)
    if not lst_tables:
        raise HTTPException(status_code=404, detail="dominotables.not_exists")
    
    # obtener escalafon de parejas.
    lst_pairs = get_list_rounds_pairs(round_id, db=db)
    
    # asociar a cada mesa los 2 parejas que le tocarian.
    lst_dist_tables = []
    amount_tables = len(lst_tables)
    for i in range(amount_tables):
        i+=1
        j=i*2-2
        table_id = lst_tables[i-1].id
        dict_tables = {'table_id': table_id, 'table_number': lst_tables[i-1].table_number, 'lst_player': []}
        for j in range(j,i*2):
            if j > len(lst_pairs)-1:
                break
            dict_tables['lst_player'].append(lst_pairs[j])
        lst_dist_tables.append(dict_tables)

    # Por cada mesa, ubicar los jugadores
    for item_tab in lst_dist_tables:
        boletus_id = str(uuid.uuid4())
        one_boletus = DominoBoletus(id=boletus_id, tourney_id=tourney_id, round_id=round_id, table_id=item_tab['table_id'],
                                    is_valid=True)
        
        one_data = DominoBoletusData(id=str(uuid.uuid4()), boletus_id=boletus_id, data_number=1)
        one_boletus.boletus_data.append(one_data)
    
        if item_tab['lst_player']:
            boletus_pair_one = DominoBoletusPairs(boletus_id=boletus_id, pairs_id=item_tab['lst_player'][0]['id'], is_initiator=True)
            one_boletus.boletus_pairs.append(boletus_pair_one)
            if len(item_tab['lst_player']) == 2:  #tengo las dos parejas por mesa
                boletus_pair_two = DominoBoletusPairs(boletus_id=boletus_id, pairs_id=item_tab['lst_player'][1]['id'],
                                                      is_initiator=False)
                one_boletus.boletus_pairs.append(boletus_pair_two)
                
            created_boletus_position(one_boletus, lst_player=item_tab['lst_player'], db=db)
                    
        db.add(one_boletus)        
    
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
