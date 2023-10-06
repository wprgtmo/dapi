# exampledata.py

import math
import random
import uuid
import shutil
import json

from datetime import datetime, timedelta
from fastapi import HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from typing import List
from domino.app import _
from domino.config.config import settings

from domino.models.enterprise.userprofile import ProfileUsers, SingleProfile, RefereeProfile, PairProfile, EventAdmonProfile
from domino.models.events.events import Event
from domino.models.events.tourney import Tourney, Players
    
from domino.schemas.enterprise.user import UserCreate

from domino.services.resources.status import get_one_by_name as get_one_status_by_name
from domino.services.resources.city import get_one_by_name as get_city_by_name
from domino.services.resources.utils import create_dir, copy_image

from domino.services.enterprise.profiletype import get_one as get_profile_type_by_id, get_one_by_name as get_profile_type_by_name
from domino.services.enterprise.users import new as new_user, get_one as get_user_by_id
from domino.services.enterprise.userprofile import get_one_default_user, get_user_for_single_profile_by_user, verify_exist_pair_player
from domino.services.enterprise.comunprofile import new_profile
from domino.services.enterprise.userprofile import get_one_profile_by_user

from domino.services.events.event import get_one_by_name as get_event_by_name
from domino.services.events.tourney import get_one_by_name as get_tourney_by_name
from domino.services.events.invitations import generate_for_tourney, get_one_by_id as get_invitation_by_id
from domino.services.events.player import get_one_by_invitation_id as get_one_player_by_invitation_id

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#region poblar BD de profiles user

def insert_user_examples(request:Request, db: Session):
    
    #Si son todos los usuarios es porque la BD se limpio desde cero y se incluyen los usuarios genericos
    
    #ususrio domino
    # lst_user = ['domino']
    
    #usuarios genericos
    lst_user = []
    lst_user.append(UserCreate(username='miry', first_name='Miraidys', last_name='Garcia Tornes', email='miry@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='richard', first_name='Richard', last_name='Mesa Romeu', email='richard@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='reiny', first_name='Reinier', last_name='Mesa Garcia', email='rey@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='roxy', first_name='Roxana', last_name='Mesa Garcia', email='roxy@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='roxley', first_name='Roxley', last_name='Ojeda Mesa', email='roxley@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='jorge', first_name='Jorge', last_name='Garcia Ballester', email='jorge@gmail.cu', country_id=1, password='Pi=3.1416'))
    data = [create_generic_user(request, item, 'Cienfuegos', db=db) for item in lst_user]
    
    lst_user = []
    lst_user.append(UserCreate(username='migue', first_name='Miguel', last_name='Lau Díaz', email='migue@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='migueldavid', first_name='Miguel David', last_name='Lau Medina', email='migued@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='milvia', first_name='Milvia', last_name='Medina', email='milvia@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='eloisa', first_name='Eloisa', last_name='Medina', email='eloisa@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='mayte', first_name='Mayte', last_name='Lau Diaz', email='mayte@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='fernandito', first_name='Fernando Miguel', last_name='Lau Díaz', email='fernandito@gmail.cu', country_id=1, password='Pi=3.1416'))
    data = [create_generic_user(request, item, 'Matanzas', db=db) for item in lst_user]
    
    lst_user = []
    lst_user.append(UserCreate(username='wilfre', first_name='Wilfredo', last_name='Perez Romero', email='wilfre@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='senen', first_name='Senen', last_name='Senen', email='senen@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='osmany', first_name='Osmany', last_name='Chicho', email='osmany@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='chicho', first_name='Chicho', last_name='Chicho', email='chicho@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='alexeis', first_name='Alexeis', last_name='Ale', email='alexeis@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='juanairis', first_name='Juana Iris', last_name='Perez', email='juana@gmail.cu', country_id=1, password='Pi=3.1416'))
    lst_user.append(UserCreate(username='aniela', first_name='Aniela', last_name='Perez', email='aniela@gmail.cu', country_id=1, password='Pi=3.1416'))
    data = [create_generic_user(request, item, 'Guantánamo', db=db) for item in lst_user]
    
    #usuarios aleatorios.
    lst_user = []
    lst_name = ['uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho']
    for item in lst_name:
        username, first_name, last_name = 'usuario.' + item, item, item
        email = 'user.' + item + '@gmail.com'
        lst_user.append(UserCreate(username=username, first_name=first_name, last_name=last_name, email=email, country_id=1, password='Pi=3.1418'))
    data = [create_generic_user(request, item, 'La Habana', db=db) for item in lst_user]
    
    lst_user = []
    lst_name = ['uno_a', 'dos_a', 'tres_a', 'cuatro_a', 'cinco_a', 'seis_a', 'siete_a', 'ocho_a']
    for item in lst_name:
        username, first_name, last_name = 'usuario.' + item, item, item
        email = 'user.' + item + '@gmail.com'
        lst_user.append(UserCreate(username=username, first_name=first_name, last_name=last_name, email=email, country_id=1, password='Pi=3.1418'))
    data = [create_generic_user(request, item, 'Artemisa', db=db) for item in lst_user]
    
    lst_user = []
    lst_name = ['uno_e', 'dos_e', 'tres_e', 'cuatro_e', 'cinco_e', 'seis_e', 'siete_e', 'ocho_e']
    for item in lst_name:
        username, first_name, last_name = 'usuario.' + item, item, item
        email = 'user.' + item + '@gmail.com'
        lst_user.append(UserCreate(username=username, first_name=first_name, last_name=last_name, email=email, country_id=1, password='Pi=3.1418'))
    data = [create_generic_user(request, item, 'Mayabeque', db=db) for item in lst_user]
    
    return True

def create_generic_user(request:Request, usercreated: UserCreate, city_name, db: Session):
    
    try:
    
        str_user = "SELECT id FROM enterprise.users where username = '" + usercreated.username + "' "
        user_id = db.execute(str_user).fetchone()
        if not user_id:   #usuario no existe
            dict_user_id = new_user(request=request, user=usercreated, db=db)
            user_id = dict_user_id.data['id']
        else:
            user_id = user_id[0]
        
        # actualizar provincias
        db_default_profile = get_one_default_user(user_id, db=db)
        
        city = get_city_by_name(city_name, db=db)
        
        if db_default_profile and city:
            db_default_profile.city_id = city.id
            db_default_profile.updated_date = datetime.now()
            db.add(db_default_profile)
            
        db.commit()    
        
    except:
        return True
    
    return True
    
def insert_others_profiles(request:Request, db: Session):
    
    lst_user_singles = ['miry', 'richard', 'reiny', 'roxy', 'roxley', 'jorge']
    lst_user_pair = [{'one_player': 'miry', 'two_player': 'richard'}, {'one_player': 'reiny', 'two_player': 'jorge'}, {'one_player': 'roxy', 'two_player': 'roxley'}]
    lst_user_referee = ['jorge']
    lst_admon = ['miry', 'richard']
    
    data = [create_single_player(request, item, 'Cienfuegos', db=db) for item in lst_user_singles]
    data = [create_pair_player(request, item, 'Cienfuegos', db=db) for item in lst_user_pair]
    data = [create_referee(request, item, 'Cienfuegos', db=db) for item in lst_user_referee]
    data = [create_event_admon(request, item, 'Cienfuegos', db=db) for item in lst_admon]
    
    lst_user_singles = ['migue', 'migueldavid', 'milvia', 'eloisa', 'mayte', 'fernandito']
    lst_user_pair = [{'one_player': 'migue', 'two_player': 'migueldavid'}, {'one_player': 'milvia', 'two_player': 'eloisa'}, {'one_player': 'mayte', 'two_player': 'fernandito'}]
    lst_user_referee = ['fernandito']
    lst_admon = ['migue']
    
    data = [create_single_player(request, item, 'Matanzas', db=db) for item in lst_user_singles]
    data = [create_pair_player(request, item, 'Matanzas', db=db) for item in lst_user_pair]
    data = [create_referee(request, item, 'Matanzas', db=db) for item in lst_user_referee]
    data = [create_event_admon(request, item, 'Matanzas', db=db) for item in lst_admon]
    
    lst_user_singles = ['wilfre', 'senen', 'osmany', 'chicho', 'alexeis', 'juanairis', 'aniela']
    lst_user_pair = [{'one_player': 'wilfre', 'two_player': 'senen'}, {'one_player': 'osmany', 'two_player': 'chicho'}, {'one_player': 'alexeis', 'two_player': 'juanairis'}]
    lst_user_referee = ['wilfre', 'senen']
    lst_admon = ['wilfre', 'senen']
    
    data = [create_single_player(request, item, 'Guantánamo', db=db) for item in lst_user_singles]
    data = [create_pair_player(request, item, 'Guantánamo', db=db) for item in lst_user_pair]
    data = [create_referee(request, item, 'Guantánamo', db=db) for item in lst_user_referee]
    data = [create_event_admon(request, item, 'Guantánamo', db=db) for item in lst_admon]
    
    lst_user_singles = []
    lst_name = ['uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho']
    lst_name_a = ['uno_a', 'dos_a', 'tres_a', 'cuatro_a', 'cinco_a', 'seis_a', 'siete_a', 'ocho_a']
    lst_name_b = ['uno_e', 'dos_e', 'tres_e', 'cuatro_e', 'cinco_e', 'seis_e', 'siete_e', 'ocho_e']
    
    for item in lst_name:
        lst_user_singles.append('usuario.' + item)
    for item in lst_name_a:
        lst_user_singles.append('usuario.' + item)
    for item in lst_name_b:
        lst_user_singles.append('usuario.' + item)
    data = [create_single_player(request, item, 'Artemisa', db=db) for item in lst_user_singles]
    
    lst_user_pair = []
    for num in range(7):
        one_player = 'usuario.' + lst_name[num]
        two_player = 'usuario.' + lst_name_a[num]
        lst_user_pair.append({'one_player': one_player, 'two_player': two_player})
    
    data = [create_pair_player(request, item, 'La Habana', db=db) for item in lst_user_pair]
    
    return True

def create_single_player(request:Request, item, city_name:str, db: Session):
    
    city = get_city_by_name(city_name, db=db)
    
    profile_type = get_profile_type_by_name("SINGLE_PLAYER", db=db)
    if not profile_type:
        return True
    
    exist_profile_id = get_one_profile_by_user(item, "SINGLE_PLAYER", db=db)
    if exist_profile_id:
        return True
    
    profile_id = get_one_profile_by_user(item, "SINGLE_PLAYER", db=db)
    
    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, profile_id, item, item, None, city.id, True, True, True, "USERPROFILE", item, item, None, is_confirmed=True,
                              single_profile_id=id)
    
    one_single_player = SingleProfile(profile_id=id, elo=0, ranking=None, level='NORMAL', updated_by=item)
    one_profile.profile_single_player.append(one_single_player)
    
    try:   
        db.add(one_profile)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        return True

def create_pair_player(request:Request, item, city_name:str, db: Session):
    
    user_principal = item['one_player']
    other_user = item['two_player']
    
    city = get_city_by_name(city_name, db=db)
    
    profile_type = get_profile_type_by_name("PAIR_PLAYER", db=db)
    if not profile_type:
        return True
    
    me_profile_id = get_user_for_single_profile_by_user(user_principal, db=db)
    if not me_profile_id:
        return True

    other_username_id = get_user_for_single_profile_by_user(other_user, db=db)
    if not other_username_id:
        return True
    
    # verificar si existe una pareja con esos dos perfles no creala..
    exist_profile = verify_exist_pair_player(me_profile_id, other_username_id, db=db)
    if exist_profile:
        return True
        
    id = str(uuid.uuid4())
    name = user_principal + '-' + other_user
    one_profile = new_profile(profile_type, id, me_profile_id, user_principal, name, None, city.id, True, True, True, 
                              "USERPROFILE", user_principal, user_principal, None, is_confirmed=True, single_profile_id=me_profile_id)
    
    one_pair_player = PairProfile(profile_id=id, level='NORMAL', updated_by=user_principal, elo=0, ranking=None)
    one_profile.profile_pair_player.append(one_pair_player)
    
    other_user_member = ProfileUsers(profile_id=other_username_id, username=other_user, is_principal=False, created_by=user_principal, is_confirmed=True,
                                    single_profile_id=other_username_id)
    one_profile.profile_users.append(other_user_member) 
    
    try:   
        db.add(one_profile)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        raise True
           
def create_referee(request:Request, item, city_name:str, db: Session):
    
    city = get_city_by_name(city_name, db=db)
    
    profile_type = get_profile_type_by_name("REFEREE", db=db)
    if not profile_type:
        return True
    
     # si ya existe perfil no permitir crear otro.
    exist_profile_id = get_one_profile_by_user(item, "REFEREE", db=db)
    if exist_profile_id:
        return True
    
    me_profile_id = get_user_for_single_profile_by_user(item, db=db)
    if not me_profile_id:
        return True

    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, me_profile_id, item, item, None, city.id, True, True, True, 
                              "REFEREE", item, item, None, is_confirmed=True, single_profile_id=me_profile_id)
    
    one_referee_user = RefereeProfile(profile_id=id, level='NORMAL', updated_by=item)
    one_profile.profile_referee_player.append(one_referee_user)
    
    path = create_dir(entity_type="USERPROFILE", user_id=str(id), entity_id=id)
    
    image_domino="public/user-vector.jpg"
    filename = str(id) + ".jpg"
    image_destiny = path + filename
    copy_image(image_domino, image_destiny)
    one_profile.photo = filename
     
    try:   
        db.add(one_profile)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        raise True
    
def create_event_admon(request:Request, item, city_name:str, db: Session):
    
    city = get_city_by_name(city_name, db=db)
    
    profile_type = get_profile_type_by_name("EVENTADMON", db=db)
    if not profile_type:
        return True
    
    # si ya existe perfil no permitir crear otro.
    exist_profile_id = get_one_profile_by_user(item, "EVENTADMON", db=db)
    if exist_profile_id:
        return True
    
    me_profile_id = get_user_for_single_profile_by_user(item, db=db)
    if not me_profile_id:
        return True
    
    default_profile_id = get_one_profile_by_user(item, db=db, profile_type='USER')
    if not default_profile_id:
        return True

    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, me_profile_id, item, item, None, city.id, True, True, True, 
                              "USERPROFILE", item, item, None, is_confirmed=True, single_profile_id=me_profile_id)
    
    one_eventadmon = EventAdmonProfile(profile_id=id, updated_by=item)
    one_profile.profile_event_admon.append(one_eventadmon)
    
    path = create_dir(entity_type="USERPROFILE", user_id=str(id), entity_id=id)
    
    try:   
        db.add(one_profile)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        raise True
 
    
#endregion


#region Events

def create_events(request:Request, db: Session):
    
    profile_admon_id = get_one_profile_by_user('miry', 'EVENTADMON', db=db)
    if not profile_admon_id:
        return True

    one_status = get_one_status_by_name('CREATED', db=db)
    if not one_status:
        return True
    
    start_date = datetime.today()
    close_date = start_date + timedelta(days=60)
    
    id = str(uuid.uuid4())
    city = get_city_by_name('La Habana', db=db)
    
    str_query = "SELECT count(id) FROM events.events Where name = 'Serie Nacional del Domino'"
    amount = db.execute(str_query).fetchone()[0]
    if amount > 0:
        return True
    
    db_event = Event(id=id, name='Serie Nacional del Domino', summary='Evento de Pruebas', start_date=start_date, 
                     close_date=close_date, registration_date=start_date, image=None, registration_price=float(0.00), 
                     city_id=city.id, main_location='Sede Principal Edificio UNO', status_id=one_status.id,
                    created_by='miry', updated_by='miry', profile_id=profile_admon_id                                                    )
    
    try:
        db.add(db_event)
        db.commit()
        return True
       
    except: 
        return True
    
def create_tourneys(request:Request, db: Session):
    
    me_profile_id = get_user_for_single_profile_by_user('miry', db=db)
    if not me_profile_id:
        return True

    one_status = get_one_status_by_name('CREATED', db=db)
    if not one_status:
        return True
    
    one_event = get_event_by_name(event_name='Serie Nacional del Domino', db=db)
    if not one_event:
        return True
    
    if one_event.status_id != one_status.id:
        return True
    
    str_query = "SELECT count(id) FROM events.tourney Where name = 'Serie Nacional del Domino.Torneo Individual'"
    amount = db.execute(str_query).fetchone()[0]
    if amount > 0:
        return True
    
    id_1 = str(uuid.uuid4())
    
    db_tourney_ind = Tourney(id=id_1, event_id=one_event.id, modality='Individual', name='Serie Nacional del Domino.Torneo Individual', 
                         summary='Torneo para jugadores individuales', start_date=one_event.start_date, 
                         status_id=one_status.id, created_by='miry', updated_by='miry', profile_id=one_event.profile_id)
    
    str_query = "SELECT count(id) FROM events.tourney Where name = 'Serie Nacional del Domino.Torneo Por Parejas'"
    amount = db.execute(str_query).fetchone()[0]
    if amount > 0:
        return True
    
    id_2 = str(uuid.uuid4())
    db_tourney_pair = Tourney(id=id_2, event_id=one_event.id, modality='Parejas', name='Serie Nacional del Domino.Torneo Por Parejas', 
                         summary='Torneo para jugadores de parejas', start_date=one_event.start_date, 
                         status_id=one_status.id, created_by='miry', updated_by='miry', profile_id=one_event.profile_id)
    
    try:
        db.add(db_tourney_ind)
        db.add(db_tourney_pair)
        db.commit()
        return True
       
    except: 
        return True
    
def created_invitations_tourneys(request:Request, db: Session):
    
    me_profile_id = get_user_for_single_profile_by_user('miry', db=db)
    if not me_profile_id:
        return True

    one_status = get_one_status_by_name('CREATED', db=db)
    if not one_status:
        return True
    
    tourney_ind = get_tourney_by_name(tourney_name='Serie Nacional del Domino.Torneo Individual', db=db)
    if not tourney_ind:
        return True
    
    tourney_pair = get_tourney_by_name(tourney_name='Serie Nacional del Domino.Torneo Por Parejas', db=db)
    if not tourney_pair:
        return True
    
    if tourney_ind.status_id != one_status.id:
        return True
    
    if tourney_pair.status_id != one_status.id:
        return True
    
    db_status_send = get_one_status_by_name('SEND', db=db)
    if not db_status_send:
        return True
    
    try:
        generate_for_tourney(tourney_ind, db_status_send, 'miry', db=db)
        generate_for_tourney(tourney_pair, db_status_send, 'miry', db=db)
        
        return True
       
    except: 
        return True
    
def accepted_invitations_tourneys(request:Request, db: Session):
    
    status_created = get_one_status_by_name('CREATED', db=db)
    if not status_created:
        return True
    
    status_acepted = get_one_status_by_name('ACCEPTED', db=db)
    if not status_acepted:
        return True
    
    str_query_sel = "SELECT inv.id invitation_id FROM events.invitations inv join events.tourney tney ON tney.id = inv.tourney_id " \
        "Where status_name = 'SEND' and tney.status_id = " + str(status_created.id)

    str_query_ind = str_query_sel + " AND tney.name = 'Serie Nacional del Domino.Torneo Individual' "
    str_query_pair = str_query_sel + " AND tney.name = 'Serie Nacional del Domino.Torneo Por Parejas' "
    
    lst_data_ind = db.execute(str_query_ind)
    lst_data_pair = db.execute(str_query_pair)
    
    for item in lst_data_ind:
        db_invitation = get_invitation_by_id(item.invitation_id, db=db)
        if not db_invitation:
            continue
        
        db_invitation.status_name = status_acepted.name
        db_invitation.updated_by = 'miry'
        db_invitation.updated_date = datetime.now()
        
        db.add(db_invitation)
    
    for item in lst_data_pair:
        db_invitation = get_invitation_by_id(item.invitation_id, db=db)
        if not db_invitation:
            continue
        
        db_invitation.status_name = status_acepted.name
        db_invitation.updated_by = 'miry'
        db_invitation.updated_date = datetime.now()
        
        db.add(db_invitation)
    
    db.commit()
        
    return True

#endregion

#region Players

def created_players(request:Request, db: Session):
    
    one_status = get_one_status_by_name('CREATED', db=db)
    if not one_status:
        return True
    
    tourney_ind = get_tourney_by_name(tourney_name='Serie Nacional del Domino.Torneo Individual', db=db)
    if not tourney_ind:
        return True
    
    tourney_pair = get_tourney_by_name(tourney_name='Serie Nacional del Domino.Torneo Por Parejas', db=db)
    if not tourney_pair:
        return True
    
    if tourney_ind.status_id != one_status.id:
        return True
    
    if tourney_pair.status_id != one_status.id:
        return True
    
    status_confirmed = get_one_status_by_name('CONFIRMED', db=db)
    if not status_confirmed:
        return True
    
    str_invs = "Select invitation_id invitation_id from events.players Where tourney_id = '"
    str_invs_ind = "SELECT * FROM events.invitations inv WHERE status_name = 'ACCEPTED' "
    
    str_query_ind = str_invs_ind + "AND tourney_id = '" + str(tourney_ind.id) + "' "
    str_query_ind += " AND inv.id NOT IN (" + str_invs + " " + str(tourney_ind.id) + "') "
    
    str_query_pair = str_invs_ind + "AND tourney_id = '" + str(tourney_pair.id) + "' "
    str_query_pair += " AND inv.id NOT IN (" + str_invs + " " + str(tourney_pair.id) + "') "
    
    lst_data_ind = db.execute(str_query_ind)
    lst_data_pair = db.execute(str_query_pair)
    
    for item in lst_data_ind:
        one_invitation = get_invitation_by_id(invitation_id=item.id, db=db)
        if not one_invitation:
            continue
        
        one_player = Players(id=str(uuid.uuid4()), tourney_id=one_invitation.tourney_id, 
                            profile_id=one_invitation.profile_id, nivel='NORMAL', invitation_id=one_invitation.id,
                            created_by='miry', updated_by='miry', is_active=True)
        
        one_invitation.updated_by = 'miry'
        one_invitation.updated_date = datetime.now()
        one_invitation.status_name = status_confirmed.name
        
        db.add(one_player)
        db.add(one_invitation)
        
    for item in lst_data_pair:
        one_invitation = get_invitation_by_id(invitation_id=item.id, db=db)
        if not one_invitation:
            continue
        
        one_player = Players(id=str(uuid.uuid4()), tourney_id=one_invitation.tourney_id, 
                            profile_id=one_invitation.profile_id, nivel='NORMAL', invitation_id=one_invitation.id,
                            created_by='miry', updated_by='miry', is_active=True)
        
        one_invitation.updated_by = 'miry'
        one_invitation.updated_date = datetime.now()
        one_invitation.status_name = status_confirmed.name
        
        db.add(one_player)
        db.add(one_invitation)
        
    
    # try:
    db.commit()
    return True
    # except (Exception, SQLAlchemyError) as e:
    #     return False
    
    
#endregion