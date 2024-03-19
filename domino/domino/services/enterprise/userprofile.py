import math
import random
import uuid
import json

from datetime import datetime

from domino.config.config import settings
from fastapi import HTTPException, Request, File
from unicodedata import name
from domino.functions_jwt import get_current_user
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.app import _

from domino.models.enterprise.user import Users
from domino.models.enterprise.userprofile import ProfileMember, ProfileUsers, SingleProfile, \
    DefaultUserProfile, RefereeProfile, PairProfile, TeamProfile, EventAdmonProfile
    
from domino.schemas.enterprise.userprofile import SingleProfileCreated, DefaultUserProfileBase, \
    RefereeProfileCreated, PairProfileCreated, TeamProfileCreated, EventAdmonProfileCreated, GenericProfileCreated
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.enterprise.profiletype import get_one as get_profile_type_by_id, get_one_by_name as get_profile_type_by_name

from domino.services.enterprise.users import get_one_by_username, get_one as get_one_user_by_id, new_from_register
from domino.services.resources.city import get_one as get_city_by_id
from domino.services.resources.country import get_one as get_country_by_id
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir, copy_image

from domino.services.enterprise.auth import get_url_avatar
from domino.services.enterprise.comunprofile import new_profile
from domino.services.federations.clubs import get_one as get_one_club

from domino.services.enterprise.comunprofile import new_profile_default_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#region Método de crear Nuevos perfiles

def new_profile_single_player(request: Request, singleprofile: SingleProfileCreated, file: File, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    profile_type = get_profile_type_by_name("SINGLE_PLAYER", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    # si ya tengo perfil no permitir crear otro.
    exist_profile_id = get_one_profile_by_user(currentUser['username'], "SINGLE_PLAYER", db=db)
    if exist_profile_id:
        raise  HTTPException(status_code=400, detail=_(locale, "userprofile.existprofile"))
    
    profile_user_id = get_one_profile_by_user(currentUser['username'], "USER", db=db)
    if not profile_user_id:
        raise  HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, currentUser['user_id'], currentUser['username'], singleprofile['name'], 
                              singleprofile['email'], singleprofile['city_id'], singleprofile['receive_notifications'], 
                              True, True, "USERPROFILE", currentUser['username'], currentUser['username'], file, is_confirmed=True,
                              single_profile_id=id)
    
    one_club = None
    if singleprofile.club_id:
        one_club = get_one_club(singleprofile.club_id, db=db)
        
    # a solicitud de Senen cuando los jugadores se creen un perfil de jugador simple, va con un elo de 1600
    one_single_player = SingleProfile(profile_id=id, elo=800, level=singleprofile['level'], updated_by=currentUser['username'],
                                      profile_user_id=profile_user_id, club_id=one_club.id if one_club else None)
    one_profile.profile_single_player.append(one_single_player)
    
    try:   
        db.add(one_profile)
        db.commit()
        result.data = {'id': id}
        return result
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.errorinsert"))

def new_profile_referee(request: Request, refereeprofile: RefereeProfileCreated, file: File, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    profile_type = get_profile_type_by_name("REFEREE", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    # si ya tengo perfil no permitir crear otro.
    exist_profile_id = get_one_profile_by_user(currentUser['username'], "REFEREE", db=db)
    if exist_profile_id:
        raise  HTTPException(status_code=400, detail=_(locale, "userprofile.existprofile"))
    
    id = str(uuid.uuid4())
    
    one_user = get_one_by_username(username=currentUser['username'], db=db)
    
    one_profile = ProfileMember(id=id, name=refereeprofile['name'], email=refereeprofile['email'] if refereeprofile['email'] else None, 
                                profile_type=profile_type.name, 
                                city_id=refereeprofile['city_id'] if refereeprofile['city_id'] else None, 
                                photo=file.filename if file else None, 
                                receive_notifications=refereeprofile['receive_notifications'], 
                                is_active=True, is_ready=True, 
                                created_by=currentUser['username'], updated_by=currentUser['username'])
    
    one_user_member = ProfileUsers(profile_id=id, username=one_user.username, is_principal=True, 
                                   created_by=currentUser['username'], is_confirmed=True)
    one_profile.profile_users.append(one_user_member)  
    
    one_referee_user = RefereeProfile(profile_id=id, level=refereeprofile['level'], updated_by=currentUser['username'])
    
    one_profile.profile_referee_player.append(one_referee_user)
    
    path = create_dir(entity_type="USERPROFILE", user_id=str(currentUser['user_id']), entity_id=id)
    
    if file:
        ext = get_ext_at_file(file.filename)
        file.filename = str(id) + "." + ext
        one_profile.photo = file.filename
        upfile(file=file, path=path)
        
    else:
        image_domino="public/user-vector.jpg"
        filename = str(id) + ".jpg"
        image_destiny = path + filename
        copy_image(image_domino, image_destiny)
        one_profile.photo = filename
        
    try:   
        db.add(one_profile)
        db.commit()
        result.data = {'id': id}
        return result
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.errorinsert"))

def verify_exist_pair_player(profile_principal_id: str, profile_secundary_id: str, db: Session):
    
    str_query = "Select count(*) from enterprise.profile_users Where single_profile_id = '" + \
        profile_secundary_id + "' and is_principal=False AND profile_id IN (Select profile_id " +\
        "from enterprise.profile_users where single_profile_id = '" + profile_principal_id + "' and is_principal=True) "
        
    amount = db.execute(str_query).fetchone()[0]
    return True if amount > 0 else False
    
def new_profile_pair_player(request: Request, pairprofile: PairProfileCreated, file: File, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    profile_type = get_profile_type_by_name("PAIR_PLAYER", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    me_profile_id = get_user_for_single_profile_by_user(currentUser['username'], db=db)
    if not me_profile_id:
        raise  HTTPException(status_code=400, detail=_(locale, "userprofile.sigle_profile_not_exist"))
    
    # verificar si existe una pareja con esos dos perfles no creala..
    if pairprofile['other_profile_id']: 
        exist_profile = verify_exist_pair_player(me_profile_id, pairprofile['other_profile_id'], db=db)
        if exist_profile:
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
    
    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, currentUser['user_id'], currentUser['username'], pairprofile['name'], 
                              pairprofile['email'], pairprofile['city_id'], pairprofile['receive_notifications'], 
                              False, True, "USERPROFILE", currentUser['username'], currentUser['username'], file, 
                              is_confirmed=True, single_profile_id=me_profile_id)
    
    one_pair_player = PairProfile(profile_id=id, level=pairprofile['level'], updated_by=currentUser['username'],
                                  elo=1600)
    one_profile.profile_pair_player.append(one_pair_player)
    
    if pairprofile['other_profile_id']:   # el segundo jugador de la pareja
        # verificar que no sea el mismo perfil que lo está creando...
        if not me_profile_id:
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_exist"))
        
        other_username = get_user_for_single_profile(pairprofile['other_profile_id'], db=db)
        if other_username:
            if me_profile_id == pairprofile['other_profile_id']:
                raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_equal"))
            
            other_user_member = ProfileUsers(profile_id=pairprofile['other_profile_id'], username=other_username, 
                                            is_principal=False, created_by=currentUser['username'], is_confirmed=False,
                                            single_profile_id=pairprofile['other_profile_id'])
            one_profile.profile_users.append(other_user_member) 
        else:
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_exist"))
    
    try:   
        db.add(one_profile)
        db.commit()
        result.data = {'id': id}
        return result
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.errorinsert"))
    
def new_profile_team_player(request: Request, teamprofile: TeamProfileCreated, file: File, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    profile_type = get_profile_type_by_name("TEAM_PLAYER", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    me_profile_id = get_user_for_single_profile_by_user(currentUser['username'], db=db)
    
    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, currentUser['user_id'], currentUser['username'], teamprofile['name'], 
                              teamprofile['email'], teamprofile['city_id'], teamprofile['receive_notifications'], 
                              False, True, "USERPROFILE", currentUser['username'], currentUser['username'], file, is_confirmed=True,
                              single_profile_id=me_profile_id)
    
    one_team_player = TeamProfile(profile_id=id, level=teamprofile['level'], amount_members=0, #teamprofile['amount_members'], 
                                  elo=1600, updated_by=currentUser['username'])
    one_profile.profile_team_player.append(one_team_player)
    
    # if int(teamprofile['amount_members']) < len(teamprofile['others_profile_id']):
    #     raise HTTPException(status_code=400, detail=_(locale, "userprofile.incorrect_amount_member"))
    
    # lst_players = json.loads(teamprofile['others_profile_id'])
    
    if teamprofile['others_profile_id']:
        
        if not me_profile_id:
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_exist"))
        
        lst_players = teamprofile['others_profile_id'].split(',')
        
        for item in lst_players: # teamprofile['others_profile_id']:
            
            other_username = get_user_for_single_profile(item, db=db)
            if other_username:
                if me_profile_id == item:
                    raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_equal"))
            
                other_user_member = ProfileUsers(profile_id=item, username=other_username, 
                                                is_principal=False, created_by=currentUser['username'],
                                                is_confirmed=False, single_profile_id=item)
                one_profile.profile_users.append(other_user_member) 
            else:
                continue
    try:   
        db.add(one_profile)
        db.commit()
        result.data = {'id': id}
        return result
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.errorinsert"))

def new_profile_event_admon(request: Request, eventadmonprofile: EventAdmonProfileCreated, file: File, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    profile_type = get_profile_type_by_name("EVENTADMON", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    me_profile_id = get_user_for_single_profile_by_user(currentUser['username'], db=db, profile_type='EVENTADMON')
    if me_profile_id:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
    
    default_profile_id = get_one_profile_by_user(currentUser['username'], db=db, profile_type='USER')
    if not default_profile_id:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_exist"))
        
    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, currentUser['user_id'], currentUser['username'], eventadmonprofile['name'], 
                              eventadmonprofile['email'], eventadmonprofile['city_id'], True, 
                              True, True, "USERPROFILE", currentUser['username'], currentUser['username'], file, is_confirmed=True,
                              single_profile_id=default_profile_id)
    
    one_eventadmon = EventAdmonProfile(profile_id=id, updated_by=currentUser['username'])
    one_profile.profile_event_admon.append(one_eventadmon)
    
    if eventadmonprofile['others_profile_id']:
        
        lst_collaborators = eventadmonprofile['others_profile_id'].split(',')
        
        for item in lst_collaborators:
            
            other_username = get_one_default_user(item, db=db)
            if other_username:
                if default_profile_id == item:
                    raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_equal"))
            
                other_user_member = ProfileUsers(profile_id=item, username=other_username.updated_by, 
                                                is_principal=False, created_by=currentUser['username'],
                                                is_confirmed=True, single_profile_id=item)
                one_profile.profile_users.append(other_user_member) 
            else:
                continue
    try:   
        db.add(one_profile)
        db.commit()
        result.data = {'id': id}
        return result
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.errorinsert"))

def new_generic_default_profile(request: Request, defaultuserprofile: DefaultUserProfileBase, db: Session, avatar: File):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    currentUser = get_current_user(request)
    
    result = ResultObject()
    
    if not defaultuserprofile['username']:
        raise HTTPException(status_code=400, detail=_(locale, "users.user_name_empty"))
    
    if not defaultuserprofile['first_name']:
        raise HTTPException(status_code=400, detail=_(locale, "users.first_name_empty"))
    
     # verificar que ese usernamer no sea ya administador que lo esta creando
    if currentUser['username'] == defaultuserprofile['username']:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
    
    #verificar que el nombre de usuario no existe en Base de Datos
    str_user = "SELECT count(username) FROM enterprise.users where username = '" + defaultuserprofile['username'] + "' "
    amount_user = db.execute(str_user).fetchone()[0]
    if amount_user > 0:
        raise HTTPException(status_code=404, detail=_(locale, "users.already_exist")) 
    
    one_country = None    
    city = get_city_by_id(defaultuserprofile['city_id'], db=db) if defaultuserprofile['city_id'] else None
    if city:
        one_country = city.country
    # else:
    #     one_country = get_country_by_id(defaultuserprofile['country_id'], db=db)
    #     if not one_country:
    #         raise HTTPException(status_code=404, detail=_(locale, "country.not_found"))
    
    id = str(uuid.uuid4())
    email = defaultuserprofile['email'] if defaultuserprofile['email'] else None
    db_user = Users(id=id, username=defaultuserprofile['username'],  first_name=defaultuserprofile['first_name'], 
                    last_name=defaultuserprofile['last_name'] if defaultuserprofile['last_name'] else None, 
                    country_id=one_country.id if one_country else None, email=email, 
                    phone=defaultuserprofile['phone'] if defaultuserprofile['phone'] else None, 
                    password=pwd_context.hash(str(settings.default_password)), is_active=True)
    
    db_user.security_code = random.randint(10000, 99999)  # codigo de 5 caracteres
    
    profile_type = get_profile_type_by_name("USER", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    full_name = defaultuserprofile['first_name'] + ' ' + defaultuserprofile['last_name'] if defaultuserprofile['last_name'] else \
        defaultuserprofile['first_name']
    
    sex = defaultuserprofile['sex'] if defaultuserprofile['sex'] else ''   
    birthdate = defaultuserprofile['birthdate'] if defaultuserprofile['birthdate'] else ''  
    alias = defaultuserprofile['alias'] if defaultuserprofile['alias'] else ''  
    job = defaultuserprofile['job'] if defaultuserprofile['sex'] else ''  
                             
    one_profile_user = new_profile_default_user(
        profile_type, id, id, defaultuserprofile['username'], full_name, email, city.id if city else None,
        False, currentUser['username'], currentUser['username'], sex, birthdate, alias, job, avatar)
    
    try:
        db.add(db_user)
        db.add(one_profile_user)
        db.commit()
        
        return result
    except (Exception, SQLAlchemyError) as e:
        if e and e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "users.already_exist")) 
        
def new_generic_event_admon(request: Request, profile_id: str, eventadmonprofile: GenericProfileCreated, file: File, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    # buscar el profile de quien lo esta creando, debe ser administrador, coger de aqui la federacion
    one_profile_admon = get_one(profile_id, db=db)
    if not one_profile_admon:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    if one_profile_admon.profile_type != 'EVENTADMON':
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.profile_incorrect"))
    
    profile_type = get_profile_type_by_name("EVENTADMON", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    # ya el usuario debe estar creado
    default_profile_id = get_one_profile_by_user(eventadmonprofile['username'], db=db, profile_type='USER')
    if not default_profile_id:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_exist"))
    
    admon_profile_id = get_user_for_single_profile_by_user(eventadmonprofile['username'], db=db, profile_type='EVENTADMON')
    if admon_profile_id:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
    
    default_profile = get_one(default_profile_id, db=db)
    
    email = eventadmonprofile['email'] if eventadmonprofile['email'] else None  
    name = eventadmonprofile['name'] if eventadmonprofile['name'] else default_profile.name  
    
    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, default_profile_id, eventadmonprofile['username'], name, 
                              email, default_profile.city_id, eventadmonprofile['receive_notifications'], 
                              True, True, "USERPROFILE", currentUser['username'], currentUser['username'], file, is_confirmed=True,
                              single_profile_id=default_profile_id)
    
    one_eventadmon = EventAdmonProfile(profile_id=id, updated_by=currentUser['username'], 
                                       federation_id=one_profile_admon.profile_event_admon[0].federation_id)
    one_profile.profile_event_admon.append(one_eventadmon)
    
    try:   
        db.add(one_profile)
        db.commit()
        result.data = {'id': id}
        return result
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.errorinsert"))
                        
#endregion
 
#region Obteniendo valores    
def get_one(id: str, db: Session):  
    return db.query(ProfileMember).filter(ProfileMember.id == id).first()

def get_profile_user_ids(profile_id: str, single_profile_id:str, db: Session):  
    return db.query(ProfileUsers).filter_by(profile_id=profile_id, single_profile_id=single_profile_id).first()

def get_one_single_profile_by_id(id: str, db: Session):  
    return db.query(SingleProfile).filter(SingleProfile.profile_id == id).first()

def get_one_default_user(id: str, db: Session):  
    return db.query(DefaultUserProfile).filter(DefaultUserProfile.profile_id == id).first()

def get_one_referee_profile_by_id(id: str, db: Session):  
    return db.query(RefereeProfile).filter(RefereeProfile.profile_id == id).first()

def get_count_user_for_status(profile_id: str, confirmed: bool, db: Session):  
    
    str_query = "Select count(us.username) FROM enterprise.profile_member pro " +\
        "join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.is_active = True and pro.id='" + profile_id + "' AND is_confirmed = " + str(confirmed)
    res_profile = db.execute(str_query).fetchone()
    return res_profile[0] if res_profile else ""

def get_user_for_single_profile(profile_id: str, db: Session):  
    
    str_query = "Select us.username FROM enterprise.profile_member pro " +\
        "join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.is_active = True and pro.id='" + profile_id + "' AND pro.profile_type = 'SINGLE_PLAYER'"
    res_profile = db.execute(str_query).fetchone()
    return res_profile[0] if res_profile else ""
    
def get_user_for_single_profile_by_user(user_name: str, db: Session, profile_type='SINGLE_PLAYER'):  
    
    str_query = "Select pro.id profile_id FROM enterprise.profile_member pro " +\
        "join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.is_active = True and us.username='" + user_name + "' AND pro.profile_type = '" + profile_type + "' "
        
    res_profile = db.execute(str_query).fetchone()
    return res_profile[0] if res_profile else ""

def get_single_profile_id_for_profile_by_user(user_name: str, profile_id: str, db: Session):  
    
    str_query = "Select us.single_profile_id FROM enterprise.profile_member pro " +\
        "join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.is_active = True and us.username='" + user_name + "' AND us.profile_id = '" + profile_id + "' "
        
    res_profile = db.execute(str_query).fetchone()
    return res_profile[0] if res_profile else ""

def get_info_owner_profile(profile_id: str, db: Session):  
    
    str_query = "Select pmem.id, pmem.name, pmem.photo , psin.elo " +\
        "from enterprise.profile_users us " +\
        "JOIN enterprise.profile_member pmem ON pmem.id = us.single_profile_id " + \
        "JOIN enterprise.profile_single_player psin ON psin.profile_id = pmem.id " +\
        "WHERE us.profile_id = '" + profile_id + "' AND us.is_principal = True "
        
    res_profile = db.execute(str_query)
    profile_id, name, photo, elo = '', '', '', ''
    for item in res_profile:
        profile_id = item.id
        name, photo = item.name, item.photo
        elo = item.elo if item.elo else ''
        
    return profile_id, name, photo, elo
    
def get_one_pair_profile(id: str, db: Session):  
    return db.query(PairProfile).filter(PairProfile.profile_id == id).first()

def get_one_team_profile(id: str, db: Session):  
    return db.query(TeamProfile).filter(TeamProfile.profile_id == id).first()

def get_all_default_profile(request:Request, profile_id: str, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    str_from = "FROM enterprise.profile_member pmem " +\
        "JOIN enterprise.profile_default_user psin ON psin.profile_id = pmem.id " +\
        "left join resources.city city ON city.id = pmem.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id "
    
    str_count = "Select count(*) " + str_from
    str_query = "Select pmem.id profile_id, pmem.name, photo, pmem.city_id, city.name city_name, city.country_id, " +\
        "pa.name as country_name " + str_from
    
    str_where = " WHERE pmem.is_active = True "  
    
    dict_query = {'name': " AND pmem.name ilike '%" + criteria_value + "%'"
                 }
    
    str_count += str_where
    str_query += str_where
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY pmem.name " 
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_single_player(item, page, db=db, api_uri=api_uri, profile_type='USER') for item in lst_data]
    
    return result

def get_all_single_profile(request:Request, profile_id: str, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    # por el perfil, buscar a que federacion pertenece
    one_profile = get_one(profile_id, db=db)
    if not one_profile:
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
    
    federation_id = None
    if one_profile.profile_type == 'EVENTADMON':
        federation_id = one_profile.profile_event_admon[0].federation_id if one_profile.profile_event_admon else None
    elif one_profile.profile_type == 'FEDERATED':
        federation_id = one_profile.profile_federated[0].federation_id if one_profile.profile_federated else None
    else:
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
    
    if not federation_id:
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
    
    str_from = "FROM enterprise.profile_member pmem " +\
        "JOIN enterprise.profile_single_player psin ON psin.profile_id = pmem.id " +\
        "left join resources.city city ON city.id = pmem.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id "
    
    str_count = "Select count(*) " + str_from
    str_query = "Select pmem.id profile_id, pmem.name, photo, pmem.city_id, city.name city_name, city.country_id, " +\
        "pa.name as country_name, psin.elo, psin.level " + str_from
    
    str_where = " WHERE pmem.is_active = True "  
    
    dict_query = {'name': " AND pmem.name ilike '%" + criteria_value + "%'",
                  'club_id': " AND psin.club_id = " + criteria_value 
                 }
    
    str_count += str_where
    str_query += str_where
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY pmem.name " 
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_single_player(item, page, db=db, api_uri=api_uri) for item in lst_data]
    return result

def get_all_eventadmon_profile(request:Request, profile_id: str, page: int, per_page: int, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    one_profile = get_one(profile_id, db=db)
    if not one_profile:
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
    
    if one_profile.profile_type != 'EVENTADMON':
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.profile_incorrect"))
    
    federation_id = one_profile.profile_event_admon[0].federation_id if one_profile.profile_event_admon else None
    if not federation_id:
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))

    str_from = "FROM enterprise.profile_member pmem " +\
        "JOIN enterprise.profile_event_admon pa ON pa.profile_id = pmem.id " +\
        "left join resources.city city ON city.id = pmem.city_id " +\
        "left join resources.country co ON co.id = city.country_id "
    
    str_count = "Select count(*) " + str_from
    str_query = "Select pmem.name, pmem.email, pmem.id profile_id, pmem.photo, " +\
        "pmem.city_id, city.name city_name, city.country_id, co.name as country_name " + str_from
    
    str_where = " WHERE pmem.is_active = True and pa.federation_id = " + str(federation_id)   

    str_search = ''
    if criteria_value:
        str_search = "AND (pa.name ilike '%" + criteria_value + "%' OR city.name ilike '%" + criteria_value +\
            "%' OR us.email ilike '%" + criteria_value + "%')"
        str_where += str_search
        
    str_count += str_where
    str_query += str_where
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY pmem.name " 
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_federation_profile(item, db=db, api_uri=api_uri) for item in lst_data]
    return result
    

def create_dict_row_single_player(item, page, db: Session, api_uri="", profile_type='SINGLE_PLAYER'):
    
    dict_row = {'profile_id': item['profile_id'], 'name': item['name'], 
               'city': item['city_id'], 'city_name': item['city_name'], 
               'country_id': item['country_id'], 'country': item['country_name'], 
               'photo' : get_url_avatar(item['profile_id'], item['photo'], api_uri=api_uri)}
    
    level_name = get_type_level(item['level']) if item['level'] else '' 
    if profile_type == 'SINGLE_PLAYER':
        dict_row['elo'] = item['elo'] if item['elo'] else '' 
        dict_row['level'] = level_name 
    
    if page != 0:
        dict_row['selected'] = False
    
    return dict_row

def create_dict_row_federation_profile(item, db: Session, api_uri=""):
    
    dict_row = {'profile_id': item['profile_id'], 'name': item['name'],
                'email': item['email'] if item['email'] else '',
                'city': item['city_id'] if item['city_id'] else '', 'city_name': item['city_name'] if item['city_name'] else '', 
                'country_id': item['country_id'] if item['country_id'] else '', 
                'country_name': item['country_name'] if item['country_name'] else '', 
                'photo' : get_url_avatar(item['profile_id'], item['photo'], api_uri=api_uri)}
    
    return dict_row

def get_one_single_profile(request: Request, id: str, db: Session): 
    
    result = ResultObject() 
    
    api_uri = str(settings.api_uri)
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description, " +\
        "city.name as city_name, city.country_id, pa.name as country_name, sing.elo, sing.level  " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_single_player sing ON sing.profile_id = pro.id " +\
        "left join resources.city city ON city.id = pro.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id " +\
        "Where pro.is_active = True AND pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, api_uri=api_uri)
        level_name = get_type_level(item.level) if item.level else '' 
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'elo': item.elo if item.elo else '', 
                       'level': level_name, 
                       'country_id': item.country_id if item.country_id else '', 
                       'country': item.country_name if item.country_name else '', 
                       'city_id': item.city_id if item.city_id else '', 
                       'city_name': item.city_name if item.city_name else '',
                       'receive_notifications': item.receive_notifications}
    
    return result

def get_one_referee_profile(request: Request, id: str, db: Session): 
    
    result = ResultObject() 
    
    api_uri = str(settings.api_uri)
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description, " +\
        "city.name as city_name, city.country_id, pa.name as country_name, sing.level " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_referee sing ON sing.profile_id = pro.id " +\
        "left join resources.city city ON city.id = pro.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id " +\
        "Where pro.is_active = True AND pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, api_uri=api_uri)
        level_name = get_type_level(item.level) if item.level else '' 
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'country_id': item.country_id if item.country_id else '', 
                       'level': level_name,
                       'country': item.country_name if item.country_name else '', 
                       'city_id': item.city_id if item.city_id else '', 
                       'city_name': item.city_name if item.city_name else '',
                       'receive_notifications': item.receive_notifications}
    
    return result

def get_one_pair_profile_by_id(request: Request, id: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    currentUser = get_current_user(request)
    
    result = ResultObject() 
    
    api_uri = str(settings.api_uri)
    
    single_profile_id = get_user_for_single_profile_by_user(currentUser['username'], db=db)
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description, " +\
        "city.name as city_name, city.country_id, pa.name as country_name, sing.elo, sing.level  " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_pair_player sing ON sing.profile_id = pro.id " +\
        "left join resources.city city ON city.id = pro.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id " +\
        "Where pro.is_active = True AND  pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, api_uri=api_uri)
        level_name = get_type_level(item.level) if item.level else '' 
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'elo': item.elo if item.elo else '', 
                       'level': level_name, 
                       'country_id': item.country_id if item.country_id else '', 
                       'country': item.country_name if item.country_name else '', 
                       'city_id': item.city_id if item.city_id else '', 
                       'city_name': item.city_name if item.city_name else '',
                       'receive_notifications': item.receive_notifications,
                       'lst_users': get_lst_users_pair_profile(item.profile_id, single_profile_id=single_profile_id, db=db)}
    
    if not result.data:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    return result

def get_one_team_profile_by_id(request: Request, id: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    currentUser = get_current_user(request)
    
    result = ResultObject() 
    
    api_uri = str(settings.api_uri)
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description, " +\
        "city.name as city_name, city.country_id, pa.name as country_name, sing.elo, sing.level  " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_team_player sing ON sing.profile_id = pro.id " +\
        "left join resources.city city ON city.id = pro.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id " +\
        "Where pro.is_active = True AND pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, api_uri=api_uri)
        level_name = get_type_level(item.level) if item.level else '' 
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'elo': item.elo if item.elo else '', 
                       'level': level_name, 
                       'country_id': item.country_id if item.country_id else '', 
                       'country': item.country_name if item.country_name else '', 
                       'city_id': item.city_id if item.city_id else '', 
                       'city_name': item.city_name if item.city_name else '',
                       'receive_notifications': item.receive_notifications,
                       'lst_users': get_lst_users_team_profile(item.profile_id, db=db)}
    
    if not result.data:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    return result

def get_one_eventadmon_profile_by_id(request: Request, id: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    currentUser = get_current_user(request)
    
    result = ResultObject() 
    
    api_uri = str(settings.api_uri)
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description, " +\
        "city.name as city_name, city.country_id, pa.name as country_name  " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_event_admon sing ON sing.profile_id = pro.id " +\
        "left join resources.city city ON city.id = pro.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id " +\
        "Where pro.is_active = True AND pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, api_uri=api_uri)
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'country_id': item.country_id if item.country_id else '', 
                       'country': item.country_name if item.country_name else '', 
                       'city_id': item.city_id if item.city_id else '', 
                       'city_name': item.city_name if item.city_name else '',
                       'receive_notifications': item.receive_notifications,
                       'lst_users': get_lst_users_team_profile(item.profile_id, db=db)}
    
    if not result.data:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    return result

def get_generic_eventadmon_profile_by_id(request: Request, id: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    api_uri = str(settings.api_uri)
    
    str_query = "Select us.username, us.first_name, us.last_name, us.email, " +\
        "pro.id profile_id, pro.city_id, us.photo, pro.receive_notifications, " +\
        "city.name as city_name, city.country_id, co.name as country_name  " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_event_admon pa ON pa.profile_id = pro.id " +\
        "JOIN enterprise.users us ON us.id = pa.profile_user_id " +\
        "left join resources.city city ON city.id = pro.city_id " +\
        "left join resources.country co ON co.id = city.country_id " +\
        "Where pro.is_active = True AND pro.id='" + id + "' "

    res_profile=db.execute(str_query)
    
    for item in res_profile:
        result.data = {'id': item.profile_id, 'first_name': item.first_name, 'last_name': item.last_name, 
                       'email': item.email, 'username': item.username, 'country_id': item.country_id if item.country_id else '', 
                       'country': item.country_name if item.country_name else '', 
                       'city_id': item.city_id if item.city_id else '', 
                       'city_name': item.city_name if item.city_name else '',
                       'photo': get_url_avatar(item.profile_id, item.photo, api_uri=api_uri)
                       }
    
    if not result.data:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    return result

def get_one_default_user_profile(request: Request, id: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    api_uri = str(settings.api_uri)
    
    str_query = "Select pro.id profile_id, username, pro.name, pro.email, def.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description, " +\
        "us.first_name, us.last_name, us.phone, us.is_active, us.country_id, " +\
        "def.job, def.sex, def.birthdate, def.alias, pa.name as country_name, " +\
        "city.id as city_id, city.name as city_name " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_default_user def ON def.profile_id = pro.id " +\
        "inner join enterprise.users us ON us.id = pro.id " +\
        "left join resources.country pa ON pa.id = us.country_id " +\
        "left join resources.city city ON city.id = def.city_id " +\
        "Where pro.is_active = True AND pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        result.data = {'id': item.profile_id, 'first_name': item.first_name, 
                       'last_name': item.last_name if item.last_name else '',  
                       'email': item.email if item.email else '', 
                       'username': item.username, 'alias': item.alias if item.alias else '',
                       'phone': item.phone if item.phone else '', 
                       'job': item.job if item.job else '', 'sex': item.sex if item.sex else '', 
                       'birthdate': item.birthdate if item.birthdate else '',
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 
                       'photo': get_url_avatar(item.profile_id, item.photo, api_uri=api_uri),
                       'country_id': item.country_id if item.country_id else '', 
                       'country': item.country_name if item.country_name else '', 
                       'city_id': item.city_id if item.city_id else '', 
                       'city_name': item.city_name if item.city_name else '',
                       'receive_notifications': item.receive_notifications}
    
    if not result.data:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
        
    return result

def get_dicc_users_team_profile(profile_id: str, db: Session): 
    
    dicc_data = {}
    
    str_query = "Select puse.single_profile_id profile_id, pmem.name " +\
        "FROM enterprise.profile_users puse " +\
        "JOIN enterprise.profile_member pmem ON pmem.id = puse.single_profile_id " +\
        "Where pmem.is_active = True AND profile_id='" + profile_id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        if item.profile_id not in dicc_data:
            dicc_data[item.profile_id] = item.name
        
    return dicc_data

def get_lst_users_team_profile(profile_id: str, db: Session): 
    
    lst_data = []
    
    api_uri = str(settings.api_uri)
    
    str_query = "Select puse.single_profile_id profile_id, pmem.name, pmem.photo, pmem.city_id, is_principal, " +\
        "city.name as city_name, city.country_id, pa.name as country_name " +\
        "FROM enterprise.profile_users puse " +\
        "JOIN enterprise.profile_member pmem ON pmem.id = puse.single_profile_id " +\
        "left join resources.city city ON city.id = pmem.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id " +\
        "Where pmem.is_active = True AND profile_id='" + profile_id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        lst_data.append({'profile_id': item.profile_id, 'name': item.name, 
                         'is_principal': item.is_principal,
                         'photo': get_url_avatar(item.profile_id, item.photo, api_uri=api_uri),
                         'country_id': item.country_id if item.country_id else '', 
                         'country': item.country_name if item.country_name else '', 
                         'city_id': item.city_id if item.city_id else '', 
                         'city_name': item.city_name if item.city_name else ''})
        
    return lst_data

def get_lst_users_pair_profile(profile_id: str, single_profile_id: str, db: Session): 
    
    dict_data = {}
    
    api_uri = str(settings.api_uri)
    
    str_query = "Select puse.single_profile_id profile_id, pmem.name, pmem.photo, pmem.city_id, is_principal, " +\
        "city.name as city_name, city.country_id, pa.name as country_name " +\
        "FROM enterprise.profile_users puse " +\
        "JOIN enterprise.profile_member pmem ON pmem.id = puse.single_profile_id " +\
        "left join resources.city city ON city.id = pmem.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id " +\
        "Where pmem.is_active = True AND profile_id='" + profile_id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        if item.profile_id == single_profile_id:
            continue
        
        dict_data = {'profile_id': item.profile_id, 'name': item.name, 
                     'is_principal': item.is_principal,
                     'photo': get_url_avatar(item.profile_id, item.photo, api_uri=api_uri),
                     'country_id': item.country_id if item.country_id else '', 
                     'country': item.country_name if item.country_name else '', 
                     'city_id': item.city_id if item.city_id else '', 
                     'city_name': item.city_name if item.city_name else ''}
        
    return dict_data
    
def get_one_profile_id(id: str, db: Session): 
    str_query = "Select pro.id FROM enterprise.profile_member pro join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.is_active = True AND pro.id='" + id + "' "
        
    res_profile_id=db.execute(str_query)
    profile_id=res_profile_id[0] if res_profile_id else ""
    return profile_id

def get_one_profile_by_user(username: str, profile_type: str, db: Session): 
    str_query = "Select pro.id FROM enterprise.profile_member pro join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.is_active = True and username='" + username + "' AND pro.profile_type = '" + profile_type + "' "
        
    res_profile_id=db.execute(str_query).fetchone()
    profile_id=res_profile_id[0] if res_profile_id else ""
    return profile_id
    
def get_all_profile_by_user_profile_id(request: Request, profile_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    currentUser = get_current_user(request)
    
    result = ResultObject() 
    result.data = []
    
    api_uri = str(settings.api_uri)
    
    db_profile = get_one(id=profile_id, db=db)
    if not db_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    try:
       
        str_profile = "SELECT DISTINCT pme.id as profile_id, profile_type, prot.description, " +\
            "pme.name, pme.photo, pme.city_id, city.country_id, pa.name as country_name, " +\
            "city.name as city_name, pme.name, pme.email, pme.photo " +\
            "FROM enterprise.profile_member pme " +\
            "INNER JOIN enterprise.profile_users pus ON pus.profile_id = pme.id " +\
            "INNER JOIN enterprise.profile_type prot ON prot.name = pme.profile_type " +\
            "left join resources.city city ON city.id = pme.city_id " +\
            "left join resources.country pa ON pa.id = city.country_id " +\
            "where pme.is_active = True and (pus.username = '" + currentUser['username'] + "' and pus.is_confirmed = True) " +\
            "AND pme.id != '" + profile_id + "' "
            
            # antes where pme.is_active = True and (pme.created_by = '" + currentUser['username'] + "' " +\
        
        lst_data =  db.execute(str_profile)
        
        for item in lst_data:
            result.data.append({'profile_id': item.profile_id, 
                                'profile_name': item.profile_type,
                                'profile_description': item.description,
                                'name': item.name,
                                'email': item.email,
                                'photo': get_url_avatar(item.profile_id, item.photo, api_uri=api_uri),
                                'country_id': item.country_id if item.country_id else '', 
                                'country': item.country_name if item.country_name else '', 
                                'city_id': item.city_id if item.city_id else '', 
                                'city_name': item.city_name if item.city_name else ''})  
     
        return result
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.imposible_delete"))

def get_all_federated_profile(request:Request, page: int, per_page: int, criteria_value: str, profile_id: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    api_uri = str(settings.api_uri)
    
    # profile_id = '812e971f-aed4-4d7c-9c79-c158b6a05a58' if not profile_id else profile_id 
    # por el perfil, buscar a que federacion pertenece
    one_profile = get_one(profile_id, db=db)
    
    if not one_profile:
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
    
    federation_id = None
    if one_profile.profile_type == 'EVENTADMON':
        federation_id = one_profile.profile_event_admon[0].federation_id if one_profile.profile_event_admon else None
    elif one_profile.profile_type == '':
        federation_id = one_profile.profile_federated[0].federation_id if one_profile.profile_federated else None
    else:
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
    
    if not federation_id:
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
    
    str_from = "FROM enterprise.profile_member pmem " +\
        "JOIN enterprise.profile_event_admon pa ON pa.profile_id = pmem.id " +\
        "JOIN federations.federations fed ON fed.id = pa.federation_id " +\
        "left join resources.city city ON city.id = pmem.city_id " +\
        "left join resources.country co ON co.id = city.country_id "
    
    str_count = "Select count(*) " + str_from
    str_query = "Select pmem.id profile_id, pmem.name, photo, pmem.city_id, city.name city_name, city.country_id, " +\
        "co.name as country_name, fed.id as federation_id, fed.name as federation_name, fed.siglas " + str_from
    
    str_where = " WHERE pmem.is_active = True "  

    str_search = ''
    if criteria_value:
        str_search = "AND (pmem.name ilike '%" + criteria_value + "%' OR city_name ilike '%" + criteria_value +\
            "%' OR fed.name ilike '%" + criteria_value + "%')"
        str_where += str_search
        
    str_count += str_where
    str_query += str_where
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    
    str_query += " ORDER BY pmem.name " 
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
     
    lst_data = db.execute(str_query)
    result.data = [create_dict_row_federation_profile(item, db=db, api_uri=api_uri) for item in lst_data]
    return result

#endregion        

#region Metodos de actualizar perfiles

def update_one_single_profile(request: Request, id: str, singleprofile: SingleProfileCreated, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_member_profile = get_one(id, db=db)
    if not db_member_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    update_profile(db_member_profile, file, currentUser, singleprofile['name'], singleprofile['email'], singleprofile['city_id'], 
                   singleprofile['receive_notifications'])
    
    db_single_profile = get_one_single_profile_by_id(id, db=db) 
    if not db_single_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
     
    try:
        db_single_profile.level = singleprofile['level'] if singleprofile['level'] else None
        
        db_member_profile.updated_by = currentUser['username']
        db_member_profile.updated_date = datetime.now()
        
        db.add(db_member_profile)
        db.add(db_single_profile)
        
        db.commit()
        
        result.data = get_url_avatar(db_member_profile.id, db_member_profile.photo)
        return result
    
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
        
def update_elo_single_profile(request: Request, profile_id: str, elo: float, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_single_profile = get_one_single_profile_by_id(profile_id, db=db) 
    if not db_single_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    try:
        db_single_profile.elo = elo
        
        db_single_profile.updated_by = currentUser['username']
        db_single_profile.updated_date = datetime.now()
        
        db.add(db_single_profile)
        db.commit()
        
        return result
    
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))

def update_one_pair_profile(request: Request, id: str, pairprofile: PairProfileCreated, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    me_profile_id = get_user_for_single_profile_by_user(currentUser['username'], db=db)
    if not me_profile_id:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_exist"))
    
    if pairprofile['other_profile_id'] and pairprofile['other_profile_id'] == me_profile_id: 
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_equal"))
    
    db_profile = get_one(id, db=db)
    if not db_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    update_profile(db_profile, file, currentUser, pairprofile['name'], pairprofile['email'], pairprofile['city_id'], 
                   pairprofile['receive_notifications'])
    
    db_pair_profile = get_one_pair_profile(db_profile.id, db=db)
    if not db_pair_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    db_pair_profile.level = pairprofile['level']
    
    db_profile.updated_by = currentUser['username']
    db_profile.updated_date = datetime.now()
    
    # actualizando la pareja
    dicc_player = get_dicc_users_team_profile(profile_id=id, db=db)
    
    if pairprofile['other_profile_id']:
        # if el jugador que viene es distinto al que tengo ya salvado, borrar primero
        if pairprofile['other_profile_id'] not in dicc_player:   # es nuevo
            # borrar el que esta
            for item_key in dicc_player:
                if me_profile_id == item_key:
                    continue   # el principal no se puede borrar
                
                db_user = db.query(ProfileUsers).filter_by(profile_id = id, single_profile_id=item_key).first()
                db.delete(db_user)
            
            other_username = get_user_for_single_profile(pairprofile['other_profile_id'], db=db)
            if other_username:
                other_user_member = ProfileUsers(profile_id=id, username=other_username, 
                                                is_principal=False, created_by=currentUser['username'],
                                                is_confirmed=False, single_profile_id=pairprofile['other_profile_id'])
                db_profile.profile_users.append(other_user_member) 
                            
    try:
        db.add(db_profile)
        db.add(db_pair_profile)
        db.commit()
        
        result.data = get_url_avatar(db_profile.id, db_profile.photo)
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
        
def update_one_team_profile(request: Request, id: str, teamprofile: TeamProfileCreated, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    me_profile_id = get_user_for_single_profile_by_user(currentUser['username'], db=db)
    if not me_profile_id:
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_exist"))
    
    db_profile = get_one(id, db=db)
    if not db_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    update_profile(db_profile, file, currentUser, teamprofile['name'], teamprofile['email'], teamprofile['city_id'], 
                   teamprofile['receive_notifications'])
    
    db_team_profile = get_one_team_profile(db_profile.id, db=db)
    if not db_team_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    db_team_profile.level = teamprofile['level']
    db_profile.updated_by = currentUser['username']
    db_profile.updated_date = datetime.now()
    
    dicc_player = get_dicc_users_team_profile(profile_id=id, db=db)
    
    if teamprofile['others_profile_id']:
        lst_players = teamprofile['others_profile_id'].split(',')
        
        for item in lst_players:
            if item not in dicc_player:   # es nuevo
                other_username = get_user_for_single_profile(item, db=db)
                if other_username:
                    if me_profile_id == item:
                        continue
                
                    other_user_member = ProfileUsers(profile_id=item, username=other_username, 
                                                    is_principal=False, created_by=currentUser['username'],
                                                    is_confirmed=False, single_profile_id=item)
                    db_profile.profile_users.append(other_user_member) 
                else:
                    continue
            else:
                continue  # es el mismo, se mantiene
            
        for item_key in dicc_player:
            if item_key not in lst_players:    # eliminar
                # si es el principal no se puede eliminar
                if me_profile_id != item_key:
                    db_user = db.query(ProfileUsers).filter_by(profile_id = id, single_profile_id=item_key).first()
                    db.delete(db_user)
                
    try:
        db.add(db_profile)
        db.add(db_team_profile)
        db.commit()
        result.data = get_url_avatar(db_profile.id, db_profile.photo)
        
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
        
def update_one_referee_profile(request: Request, id: str, refereeprofile: RefereeProfileCreated, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_profile = get_one(id, db=db)
    if not db_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    update_profile(db_profile, file, currentUser, refereeprofile['name'], refereeprofile['email'], refereeprofile['city_id'], 
                   refereeprofile['receive_notifications'])
    
    db_referee_profile = get_one_referee_profile_by_id(db_profile.id, db=db)
    db_referee_profile.level = refereeprofile['level']
    
    db_profile.updated_by = currentUser['username']
    db_profile.updated_date = datetime.now()
        
    try:
        db.add(db_profile)
        db.add(db_referee_profile)
        db.commit()
        result.data = get_url_avatar(db_profile.id, db_profile.photo)
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
        
def update_one_default_profile(request: Request, id: str, defaultuserprofile: DefaultUserProfileBase, db: Session, avatar: File):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    currentUser = get_current_user(request)
    
    result = ResultObject()
    
    db_default_profile = get_one(id, db=db)
    if not db_default_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
       
    one_user = get_one_user_by_id(user_id=id, db=db)
    if not one_user:
        raise HTTPException(status_code=400, detail=_(locale, "user.not_found"))
    
    db_default_profile_user = get_one_default_user(id, db=db)
    if not db_default_profile_user:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    if 'first_name' in defaultuserprofile and defaultuserprofile['first_name'] and \
        defaultuserprofile['first_name'] != '' and one_user.first_name != defaultuserprofile['first_name']:
        one_user.first_name = defaultuserprofile['first_name']
        
    if 'last_name' in defaultuserprofile and defaultuserprofile['last_name'] and defaultuserprofile['last_name'] != '' \
        and one_user.last_name != defaultuserprofile['last_name']:
        one_user.last_name = defaultuserprofile['last_name']
        
    db_default_profile.name = defaultuserprofile['first_name'] + ' ' + defaultuserprofile['last_name'] if defaultuserprofile['last_name'] else one_user.last_name
    
    if 'email' in defaultuserprofile and defaultuserprofile['email'] and defaultuserprofile['email'] != '' \
        and one_user.email != defaultuserprofile['email']:
        one_user.email = defaultuserprofile['email']
        db_default_profile.email = defaultuserprofile['email']
    
    if 'phone' in defaultuserprofile and defaultuserprofile['phone'] and defaultuserprofile['phone'] != '' \
        and one_user.phone != defaultuserprofile['phone']:
        one_user.phone = defaultuserprofile['phone']
    
    if 'city_id' in defaultuserprofile and defaultuserprofile['city_id'] and defaultuserprofile['city_id'] != '' \
        and db_default_profile_user.city_id != defaultuserprofile['city_id']:
        one_city = get_city_by_id(defaultuserprofile['city_id'], db=db)
        if not one_city:
            raise HTTPException(status_code=404, detail=_(locale, "city.not_found"))
        db_default_profile.city_id = defaultuserprofile['city_id']
        db_default_profile_user.city_id = defaultuserprofile['city_id']
        one_user.country_id = one_city.country_id
        
    if 'sex' in defaultuserprofile and defaultuserprofile['sex'] and defaultuserprofile['sex'] != '' \
        and db_default_profile_user.sex != defaultuserprofile['sex']:
        db_default_profile_user.sex = defaultuserprofile['sex']
        
    if 'birthdate' in defaultuserprofile and defaultuserprofile['birthdate'] and defaultuserprofile['birthdate']  != '' \
        and db_default_profile_user.birthdate != defaultuserprofile['birthdate']:
        db_default_profile_user.birthdate = defaultuserprofile['birthdate']
        
    if 'alias' in defaultuserprofile and defaultuserprofile['alias'] and defaultuserprofile['alias'] != '' \
        and db_default_profile_user.alias != defaultuserprofile['alias']:
        db_default_profile_user.alias = defaultuserprofile['alias']
        
    if 'job' in defaultuserprofile and defaultuserprofile['job'] and defaultuserprofile['job'] != '' \
        and db_default_profile_user.job != defaultuserprofile['job']:
        db_default_profile_user.job = defaultuserprofile['job']
        
    db_default_profile.receive_notifications = defaultuserprofile['receive_notifications'] 
    
    path = create_dir(entity_type="USER", user_id=str(one_user.id), entity_id=None)  
    current_image = db_default_profile.photo
      
    if avatar:
        ext = get_ext_at_file(avatar.filename)
        avatar.filename = str(uuid.uuid4()) + "." + ext if ext else str(uuid.uuid4())
        db_default_profile.photo = avatar.filename
        path_del = "/public/profile/" + str(one_user.id) + "/" 
        try:
            del_image(path=path_del, name=str(current_image))
        except:
            pass
        upfile(file=avatar, path=path)
        
    else:
        # si no viene imagen, borrar la que tiene y poner la foto por defecto del sistema
        path_del = "/public/profile/" + str(one_user.id) + "/" 
        try:
            del_image(path=path_del, name=str(current_image))
        except:
            pass
        
        image_domino="public/user-vector.jpg"
        filename = str(db_default_profile.id) + ".jpg"
        image_destiny = "public/profile/" + str(db_default_profile.id) + "/" + str(filename)
    
        copy_image(image_domino, image_destiny)
        db_default_profile.photo = filename
    
    db_default_profile.updated_by = currentUser['username']
    db_default_profile.updated_date = datetime.now()
    
    one_user.updated_by = currentUser['username']
    one_user.updated_date = datetime.now()
        
    try:
        db.add(db_default_profile)
        db.add(one_user)
        db.add(db_default_profile_user)
        db.commit()
        
        filename = avatar.filename if avatar else str(db_default_profile.id) + ".jpg"
            
        result.data = get_url_avatar(db_default_profile.id, filename)
        return result
    except (Exception, SQLAlchemyError) as e:
        if e and e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "users.already_exist"))    

def update_profile(profile_member: ProfileMember, file: File, currentUser, name: str, email: str, city_id: int, 
                   receive_notifications: bool=None):
    
    if profile_member.name != name:
        profile_member.name = name
        
    if profile_member.email != email:
        profile_member.email = email
        
    if profile_member.city_id != city_id:
        profile_member.city_id = city_id
  
    if receive_notifications:      
        profile_member.receive_notifications = receive_notifications
    
    path = create_dir(entity_type="USERPROFILE", user_id=str(currentUser['user_id']), entity_id=profile_member.id)  
    current_image = profile_member.photo
      
    if file:
        ext = get_ext_at_file(file.filename)
        file.filename = str(uuid.uuid4()) + "." + ext if ext else str(uuid.uuid4())
        profile_member.photo = file.filename
        path_del = "/public/profile/" + str(profile_member.id) + "/"
        try:
            del_image(path=path_del, name=str(current_image))
        except:
            pass
        upfile(file=file, path=path)
        
    else:
        # si no viene imagen, borrar la que tiene y poner la foto por defecto del sistema
        
        path_del = "/public/profile/" + str(profile_member.id) + "/" 
        try:
            del_image(path=path_del, name=str(current_image))
        except:
            pass
        
        image_domino="public/user-vector.jpg"
        filename = str(profile_member.id) + ".jpg"
        image_destiny = "public/profile/" + str(profile_member.id) + "/" + str(filename)
    
        copy_image(image_domino, image_destiny)
        profile_member.photo = filename
        
    return True

def update_one_event_admon_profile(request: Request, id: str, eventadmonprofile: EventAdmonProfileCreated, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    default_profile_id = get_one_profile_by_user(currentUser['username'], db=db, profile_type='USER')
    if not default_profile_id:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_exist"))
    
    db_profile = get_one(default_profile_id, db=db)
    if not db_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    update_profile(db_profile, file, currentUser, eventadmonprofile['name'], eventadmonprofile['email'], eventadmonprofile['city_id'], 
                   True)
    
    db_profile.updated_by = currentUser['username']
    db_profile.updated_date = datetime.now()
    
    dicc_player = get_dicc_users_team_profile(profile_id=id, db=db)
    
    if eventadmonprofile['others_profile_id']:
        lst_collaborators = eventadmonprofile['others_profile_id'].split(',')
        
        for item in lst_collaborators:
            if item not in dicc_player:   # es nuevo
                other_username = get_one_default_user(item, db=db)
                if other_username:
                    if default_profile_id == item:
                        continue
                
                    other_user_member = ProfileUsers(profile_id=item, username=other_username.updated_by, 
                                                    is_principal=False, created_by=currentUser['username'],
                                                    is_confirmed=True, single_profile_id=item)
                    db_profile.profile_users.append(other_user_member) 
                else:
                    continue
            else:
                continue  # es el mismo, se mantiene
            
        for item_key in dicc_player:
            if item_key not in lst_collaborators:    # eliminar
                # si es el principal no se puede eliminar
                if default_profile_id != item_key:
                    db_user = db.query(ProfileUsers).filter_by(profile_id = id, single_profile_id=item_key).first()
                    db.delete(db_user)
                
    try:
        db.add(db_profile)
        db.commit()
        result.data = get_url_avatar(db_profile.id, db_profile.photo)
        
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))

def update_generic_event_admon_profile(request: Request, id: str, eventadmonprofile: EventAdmonProfileCreated, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_profile = get_one(id, db=db)
    if not db_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    email = eventadmonprofile['email'] if eventadmonprofile['email'] else None  
    name = eventadmonprofile['name'] if eventadmonprofile['name'] else db_profile.name  
    
    update_profile(db_profile, file, currentUser, name, email, db_profile.city_id)
    
    db_profile.updated_by = currentUser['username']
    db_profile.updated_date = datetime.now()
    
    try:
        db.add(db_profile)
        db.commit()
        result.data = get_url_avatar(db_profile.id, db_profile.photo)
        
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
                        
#endregion

#region Metodo de borrado de perfiles
         
def delete_one_default_profile(request: Request, id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    try:
        db_profile = db.query(ProfileMember).filter(ProfileMember.id == id).first()
        if not db_profile:
            raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
        
        db_user = get_one_user_by_id(user_id=id, db=db)
        if not db_user:
            raise HTTPException(status_code=400, detail=_(locale, "user.not_found"))
        
        remove_profile_member(db_profile, currentUser)
        
        db_user.is_active = False
        db_user.updated_by = currentUser['username']
        db_user.updated_date = datetime.now()
        
        db.commit()
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.imposible_delete"))

def delete_one_profile(request: Request, id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    try:
        db_profile = db.query(ProfileMember).filter(ProfileMember.id == id).first()
        if not db_profile:
            raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
        
        remove_profile_member(db_profile, currentUser)
        db.commit()
        return result
    
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.imposible_delete"))
                
def remove_profile_member(db_profile: ProfileMember, currentUser):
    
    db_profile.is_active = False
    db_profile.updated_by = currentUser['username']
    db_profile.updated_date = datetime.now()
    
    if db_profile.photo:
        path = "/public/profile/" + str(db_profile.id) + "/"
        try:
            del_image(path=path, name=str(db_profile.photo))
        except:
            pass
        try:
            remove_dir(path=path[:-1])
        except:
            pass
        
    return True

def get_type_level(level_name):
    
    # dict_result = {'rookie': 'Novato', 'professional': 'Profesional', 'expert': 'Experto'}
    dict_result = {'rookie': 'TRES', 'professional': 'DOS', 'expert': 'UNO'}
    if level_name not in dict_result:
        return level_name
    else:
        return dict_result[level_name]
    
      
#endregion
