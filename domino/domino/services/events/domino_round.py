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

from domino.models.events.domino_round import DominoRounds, DominoRoundsPairs
from domino.models.events.tourney import SettingTourney

from domino.schemas.events.events import EventBase, EventSchema
from domino.schemas.resources.result_object import ResultObject

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
from domino.services.enterprise.users import get_one_by_username
from domino.services.enterprise.userprofile import get_one as get_one_profile
from domino.services.events.domino_boletus import created_boletus_for_round
# from domino.services.events.tourney import get_one as get_one_tourney
                         
def get_all(request:Request, tourney_id:str, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    # verificar que el perfil sea admon del evento al cual pertenece el torneo.
    # db_member_profile = get_one_profile(id=profile_id, db=db)
    # if not db_member_profile:
    #     raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
   
    # if db_member_profile.profile_type != 'EVENTADMON':
    #     raise HTTPException(status_code=400, detail=_(locale, "userprofile.user_not_event_admon"))
    
    str_from = "FROM events.domino_rounds drounds " +\
        "JOIN events.tourney dtou ON dtou.id = drounds.tourney_id " +\
        "JOIN resources.entities_status sta ON sta.id = drounds.status_id " 
        
    str_count = "Select count(*) " + str_from
    str_query = "Select drounds.id, round_number, drounds.summary, drounds.start_date, drounds.close_date, " + \
        "sta.name as status_name, sta.description as status_description " + str_from
    
    str_where = " WHERE drounds.tourney_id = '" + tourney_id + "' "  
    
    dict_query = {'round_number': " AND round_number = " + criteria_value}
    
    str_count += str_where
    str_query += str_where
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY round_number ASC " 
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    result.data = [create_dict_row(item) for item in lst_data]
    
    return result

def create_dict_row(item, amount_tables=0, amount_pairs=0):
    
    new_row = {'id': item['id'], 'round_number': item['round_number'], 
               'summary': item['summary'], 'start_date': item['start_date'].strftime('%d-%m-%Y'),
               'status_name': item['status_name'], 'status_description': item['status_description'], 
               'close_date': item['close_date'].strftime('%d-%m-%Y') if str(item['status_name']) == 'FINALIZED' else ''}
    
    if amount_tables:
        new_row['amount_tables'] = amount_tables
        new_row['amount_pairs'] = amount_pairs
        
    return new_row

def get_one(round_id: str, db: Session):  
    return db.query(DominoRounds).filter(DominoRounds.id == round_id).first()

def get_one_by_id(round_id: str, db: Session): 
    result = ResultObject()  
    
    one_round = get_one(round_id, db=db)
    if not one_round:
        raise HTTPException(status_code=404, detail="dominoround.not_found")
    
    str_query = "Select drounds.id, round_number, drounds.summary, drounds.start_date, drounds.close_date, " +\
        "sta.name as status_name, sta.description as status_description " +\
        "FROM events.domino_rounds drounds " +\
        "JOIN events.tourney dtou ON dtou.id = drounds.tourney_id " +\
        "JOIN resources.entities_status sta ON sta.id = drounds.status_id " +\
        " WHERE drounds.id = '" + round_id + "' "  
        
    lst_data = db.execute(str_query) 
    
    str_amount_tables = "Select count(*) from events.domino_boletus where round_id = '" + str(round_id) + "' "
    amount_tables = db.execute(str_amount_tables).fetchone()[0]
    
    str_amount_pairs = "Select count(*) from events.domino_rounds_pairs where round_id = '" + str(round_id) + "' "
    amount_pairs=db.execute(str_amount_pairs).fetchone()[0]
    
    for item in lst_data:
        result.data = create_dict_row(item, amount_tables=amount_tables, amount_pairs=amount_pairs)
        
    if not result.data:
        raise HTTPException(status_code=404, detail="dominoround.not_found")
    
    return result

def get_first_by_tourney(tourney_id: str, db: Session): 
    
    str_query = "SELECT id FROM events.domino_rounds Where tourney_id = '" + tourney_id + "' ORDER BY round_number ASC limit 1 " 
    round_id = db.execute(str_query).fetchone()
    
    if not round_id:
        raise HTTPException(status_code=404, detail="dominoround.not_found")
    
    return round_id[0]

def configure_new_rounds(db_tourney, summary:str, db:Session, created_by:str):
  
    str_number = "SELECT round_number FROM events.domino_rounds where tourney_id = '" + db_tourney.id + "' " +\
        "ORDER BY round_number DESC LIMIT 1; "
    last_number = db.execute(str_number).fetchone()
    
    round_number = 1 if not last_number else int(last_number) + 1
    
    status_creat = get_one_status_by_name('CREATED', db=db)
    
    id = str(uuid.uuid4())
    db_round = DominoRounds(id=id, tourney_id=db_tourney.id, round_number=round_number, summary=summary,
                            start_date=datetime.now(), close_date=datetime.now(), created_by=created_by, 
                            updated_by=created_by, created_date=datetime.now(), updated_date=datetime.now(),
                            status_id=status_creat.id)
    
    try:
        db.add(db_round)
        db.commit()
        return True
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        return False
    
def delete(request: Request, round_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_round = get_one(round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "dominoround.not_found"))
    
    status_canc = get_one_status_by_name('CANCELLED', db=db)
        
    change_status_round(db_round, status_canc, currentUser['username'], db=db)
    
    return result

def start_round(request: Request, round_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    db_round = get_one(round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "dominoround.not_found"))
    
    status_init = get_one_status_by_name('INITIADED', db=db)
    
    change_status_round(db_round, status_init, currentUser['username'], db=db)
    
    return result

def close_round(request: Request, round_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
    
    db_round = get_one(round_id, db=db)
    if not db_round:
        raise HTTPException(status_code=404, detail=_(locale, "dominoround.not_found"))
    
    status_init = get_one_status_by_name('FINALIZED', db=db)
    
    change_status_round(db_round, status_init, currentUser['username'], db=db)
    
    return result
            
def change_status_round(db_round, status, username, db: Session):
    
    db_round.sttaus_id = status.id
    db_round.updated_by = username
    db_round.updated_date = datetime.now()
            
    try:
        db.add(db_round)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        return False

def create_pair_for_rounds(tourney_id: str, round_id: str, modality:str, db: Session):
    
    str_scale = "Select player_id from events.domino_rounds_scale where tourney_id = '" + tourney_id + "' " +\
        "and round_id = '" + round_id + "' order by position_number ASC "
    
    lst_scale = db.execute(str_scale).fetchall()
    
    str_select = "Select Round(SUM(elo)/2,4) as elo " if modality == 'Parejas' else 'Select elo '
    str_select += "FROM events.players play JOIN enterprise.profile_users puse ON puse.profile_id = play.profile_id " +\
        "JOIN enterprise.profile_single_player splay ON splay.profile_id = puse.single_profile_id "
    
    str_update = "UPDATE events.domino_rounds_scale SET elo = "
    str_all_update = ''
    for item in lst_scale:
        str_find = str_select + " where id = '" + item.player_id + "' "
        elo = db.execute(str_find).fetchone()
        if elo:
            str_one_update = str_update + str(elo[0]) + " where player_id = '" + item.player_id + "'; "
            str_all_update += str_one_update
    
    if str_all_update:
        db.execute(str_all_update)
        db.commit()
        
    return True

def created_one_pair(tourney_id:str, round_id:str, one_player_id:str, two_player_id:str, name:str, profile_type:str,
                     created_by:str, db: Session, position_number:int, scale_number_one_player:int, 
                     scale_number_two_player:int, player_id:str=None):
    
    one_pair = DominoRoundsPairs(id=str(uuid.uuid4()), tourney_id=tourney_id, round_id=round_id, one_player_id=one_player_id,
                                 two_player_id=two_player_id, name=name, profile_type=profile_type, player_id=player_id,
                                 position_number=position_number, 
                                 scale_number_one_player=scale_number_one_player, scale_number_two_player=scale_number_two_player,
                                 created_by=created_by, updated_by=created_by, 
                                 created_date=datetime.today(), updated_date=datetime.today(), is_active=True)
    
    db.add(one_pair)
        
    return True

def create_pair_for_profile_pair(tourney_id: str, round_id: str, db: Session, created_by: str):
    
    str_user = "Select mmb.name, puse.single_profile_id as profile_id, rsca.player_id, rsca.position_number  " +\
        "from events.domino_rounds_scale rsca " +\
        "JOIN events.players play ON play.id = rsca.player_id " +\
        "JOIN enterprise.profile_member mmb ON play.profile_id = mmb.id " +\
        "JOIN enterprise.profile_users puse ON puse.profile_id = mmb.id " +\
        "Where rsca.tourney_id = '" + tourney_id + "' AND rsca.round_id = '" + round_id + "' order by rsca.position_number ASC "
    
    lst_pair = db.execute(str_user)
    dict_pair = {}
    position_number=0
    for item in lst_pair:
        if item.name not in dict_pair:
            dict_pair[item.name] = {'player_id': item.player_id, 'scale_number': item.position_number, 'users': []}
        dict_pair[item.name]['users'].append(item.profile_id)
        
    for item_key, item_value in dict_pair.items():
        position_number+=1
        created_one_pair(tourney_id, round_id, item_value['users'][0], item_value['users'][1], item_key, 
                         'Parejas', created_by=created_by, db=db, position_number=position_number, 
                         scale_number_one_player=item_value['scale_number'], 
                         scale_number_two_player=item_value['scale_number'], player_id=item_value['player_id'])    
    return True

def create_pair_for_profile_single(tourney_id: str, round_id: str, db: Session, created_by: str):
    
    str_user = "Select mmb.name, puse.single_profile_id as profile_id, rsca.player_id, rsca.position_number " +\
        "from events.domino_rounds_scale rsca " +\
        "JOIN events.players play ON play.id = rsca.player_id " +\
        "JOIN enterprise.profile_member mmb ON play.profile_id = mmb.id " +\
        "JOIN enterprise.profile_users puse ON puse.profile_id = mmb.id " +\
        "Where rsca.tourney_id = '" + tourney_id + "' AND rsca.round_id = '" + round_id + "' order by rsca.position_number ASC "
    
    lst_pair = db.execute(str_user)
    lst_all_pair = []
    for item in lst_pair:
        lst_all_pair.append({'name': item.name, 'player_id': item.player_id, 
                             'profile_id': item.profile_id, 'scale_number': item.position_number})
    
    lst_par, lst_impar, pos = [], [], 0
    for i in lst_all_pair:   
        if  pos % 2 == 0:
            lst_par.append(lst_all_pair[pos])
        else:
            lst_impar.append(lst_all_pair[pos])
        pos+=1 
        
    amount_pair_div = divmod(len(lst_all_pair),2)
    position_number=0
    
    for num in range(0, amount_pair_div[0]-1, 2):
        position_number+=1
        name = lst_par[num]['name'] + " - " + lst_par[num+1]['name']
        created_one_pair(tourney_id, round_id, lst_par[num]['profile_id'], lst_par[num+1]['profile_id'], name, 
                         'Individual', created_by=created_by, db=db, position_number=position_number, 
                         scale_number_one_player=lst_par[num]['scale_number'],
                         scale_number_two_player=lst_par[num+1]['scale_number'], player_id=None)
        position_number+=1
        name = lst_impar[num]['name'] + " - " + lst_impar[num+1]['name']
        created_one_pair(tourney_id, round_id, lst_impar[num]['profile_id'], lst_impar[num+1]['profile_id'], name, 
                         'Individual', created_by=created_by, db=db, position_number=position_number, 
                         scale_number_one_player=lst_impar[num]['scale_number'],
                         scale_number_two_player=lst_impar[num+1]['scale_number'], player_id=None)

    if  amount_pair_div[1] > 0:  # parejas impar  
        created_one_pair(tourney_id, round_id, lst_par[len(lst_par)-1]['profile_id'], None, 
                         lst_par[len(lst_par)-1]['name'], 'Individual', created_by=created_by, 
                         db=db, position_number=position_number+1, 
                         scale_number_one_player=lst_par[len(lst_par)-1]['scale_number'],
                         scale_number_two_player=None, player_id=None) 
            
    return True
    
def configure_rounds(tourney_id: str, round_id: str, modality:str, db: Session):

    # si la modalidad es pareja, es vaciar la tabla del escalafón.
    # si es individual, aplico el algoritmo de distribuir por mesas...
    
    if modality == 'Parejas':
        create_pair_for_profile_pair(tourney_id, round_id, db=db, created_by='miry')
    else:
        create_pair_for_profile_single(tourney_id, round_id, db=db, created_by='miry')
        
    db.commit()    
    
    return True           

