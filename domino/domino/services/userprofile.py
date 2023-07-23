import math
import uuid
import json

from datetime import datetime

from domino.config.config import settings
from fastapi import HTTPException, Request, File
from unicodedata import name
from domino.functions_jwt import get_current_user
from fastapi import HTTPException
from domino.models.userprofile import ProfileMember, ProfileUsers, SingleProfile, DefaultUserProfile, RefereeProfile, PairProfile, TeamProfile
from domino.schemas.userprofile import SingleProfileCreated, DefaultUserProfileBase, RefereeProfileCreated, PairProfileCreated, TeamProfileCreated
from domino.schemas.result_object import ResultObject, ResultData
from domino.services.profiletype import get_one as get_profile_type_by_id, get_one_by_name as get_profile_type_by_name
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.app import _
from domino.services.users import get_one_by_username, get_one as get_one_user_by_id
from domino.services.city import get_one as get_city_by_id
from domino.services.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir, copy_image

from domino.services.auth import get_url_avatar
from domino.services.comunprofile import new_profile

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
    
    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, currentUser['user_id'], currentUser['username'], singleprofile['name'], 
                              singleprofile['email'], singleprofile['city_id'], singleprofile['receive_notifications'], 
                              True, True, "USERPROFILE", currentUser['username'], currentUser['username'], file, is_confirmed=True,
                              single_profile_id=id)
    
    one_single_player = SingleProfile(profile_id=id, elo=0, ranking=None, level=singleprofile['level'], updated_by=currentUser['username'])
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
        image_domino="public/profile/user-vector.jpg"
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

def new_profile_pair_player(request: Request, pairprofile: PairProfileCreated, file: File, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    profile_type = get_profile_type_by_name("PAIR_PLAYER", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    me_profile_id = get_user_for_single_profile_by_user(currentUser['username'], db=db)
    
    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, currentUser['user_id'], currentUser['username'], pairprofile['name'], 
                              pairprofile['email'], pairprofile['city_id'], pairprofile['receive_notifications'], 
                              True, True, "USERPROFILE", currentUser['username'], currentUser['username'], file, 
                              is_confirmed=True, single_profile_id=me_profile_id)
    
    one_pair_player = PairProfile(profile_id=id, level=pairprofile['level'], updated_by=currentUser['username'],
                                  elo=0, ranking=None)
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
                              True, True, "USERPROFILE", currentUser['username'], currentUser['username'], file, is_confirmed=True,
                              single_profile_id=me_profile_id)
    
    one_team_player = TeamProfile(profile_id=id, level=teamprofile['level'], amount_members=0, #teamprofile['amount_members'], 
                                  elo=0, ranking=None, updated_by=currentUser['username'])
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
        "Where pro.is_active = True and pro.id='" + profile_id + "' AND is_confirmed = " + confirmed
    res_profile = db.execute(str_query).fetchone()
    return res_profile[0] if res_profile else ""

def get_user_for_single_profile(profile_id: str, db: Session):  
    
    str_query = "Select us.username FROM enterprise.profile_member pro " +\
        "join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.is_active = True and pro.id='" + profile_id + "' AND pro.profile_type = 'SINGLE_PLAYER'"
    res_profile = db.execute(str_query).fetchone()
    return res_profile[0] if res_profile else ""
    
def get_user_for_single_profile_by_user(user_name: str, db: Session):  
    
    str_query = "Select pro.id profile_id FROM enterprise.profile_member pro " +\
        "join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.is_active = True and us.username='" + user_name + "' AND pro.profile_type = 'SINGLE_PLAYER'"
        
    res_profile = db.execute(str_query).fetchone()
    return res_profile[0] if res_profile else ""

def get_single_profile_id_for_profile_by_user(user_name: str, profile_id: str, db: Session):  
    
    str_query = "Select us.single_profile_id FROM enterprise.profile_member pro " +\
        "join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.is_active = True and us.username='" + user_name + "' AND us.profile_id = '" + profile_id + "' "
        
    res_profile = db.execute(str_query).fetchone()
    return res_profile[0] if res_profile else ""
    
def get_one_pair_profile(id: str, db: Session):  
    return db.query(PairProfile).filter(PairProfile.profile_id == id).first()

def get_one_team_profile(id: str, db: Session):  
    return db.query(TeamProfile).filter(TeamProfile.profile_id == id).first()

def get_all_single_profile(request:Request, profile_id: str, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    str_from = "FROM enterprise.profile_member pmem " +\
        "JOIN enterprise.profile_single_player psin ON psin.profile_id = pmem.id " +\
        "left join resources.city city ON city.id = pmem.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id "
    
    str_count = "Select count(*) " + str_from
    str_query = "Select pmem.id profile_id, pmem.name, photo, pmem.city_id, city.name city_name, city.country_id, " +\
        "pa.name as country_name, psin.elo, psin.ranking, psin.level " + str_from
    
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
    result.data = [create_dict_row_single_player(item, page, db=db, host=host, port=port) for item in lst_data]
    
    return result

def create_dict_row_single_player(item, page, db: Session, host="", port=""):
    
    new_row = {'profile_id': item['profile_id'], 'name': item['name'], 
               'elo': item['elo'], 'ranking': item['ranking'], 'level': item['level'], 
               'city': item['city_id'], 'city_name': item['city_name'], 
               'country_id': item['country_id'], 'country': item['country_name'], 
               'photo' : get_url_avatar(item['profile_id'], item['photo'], host=host, port=port)}
    if page != 0:
        new_row['selected'] = False
    
    return new_row

def get_one_single_profile(request: Request, id: str, db: Session): 
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description, " +\
        "city.name as city_name, city.country_id, pa.name as country_name, sing.elo, sing.ranking, sing.level  " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_single_player sing ON sing.profile_id = pro.id " +\
        "left join resources.city city ON city.id = pro.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id " +\
        "Where pro.is_active = True AND pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, host=host, port=port)
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'elo': item.elo if item.elo else '', 
                       'ranking': item.ranking if item.ranking else '', 
                       'level': item.level if item.level else '', 
                       'country_id': item.country_id if item.country_id else '', 
                       'country': item.country_name if item.country_name else '', 
                       'city_id': item.city_id if item.city_id else '', 
                       'city_name': item.city_name if item.city_name else '',
                       'receive_notifications': item.receive_notifications}
    
    return result

def get_one_referee_profile(request: Request, id: str, db: Session): 
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
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
        photo = get_url_avatar(item.profile_id, item.photo, host=host, port=port)
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'country_id': item.country_id if item.country_id else '', 
                       'level': item.level if item.level else '',
                       'country': item.country_name if item.country_name else '', 
                       'city_id': item.city_id if item.city_id else '', 
                       'city_name': item.city_name if item.city_name else '',
                       'receive_notifications': item.receive_notifications}
    
    return result

def get_one_pair_profile_by_id(request: Request, id: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    currentUser = get_current_user(request)
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    single_profile_id = get_user_for_single_profile_by_user(currentUser['username'], db=db)
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description, " +\
        "city.name as city_name, city.country_id, pa.name as country_name, sing.elo, sing.ranking, sing.level  " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_pair_player sing ON sing.profile_id = pro.id " +\
        "left join resources.city city ON city.id = pro.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id " +\
        "Where pro.is_active = True AND  pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, host=host, port=port)
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'elo': item.elo if item.elo else '', 
                       'ranking': item.ranking if item.ranking else '', 
                       'level': item.level if item.level else '', 
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
    
    single_profile_id = get_user_for_single_profile_by_user(currentUser['username'], db=db)
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description, " +\
        "city.name as city_name, city.country_id, pa.name as country_name, sing.elo, sing.ranking, sing.level  " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_team_player sing ON sing.profile_id = pro.id " +\
        "left join resources.city city ON city.id = pro.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id " +\
        "Where pro.is_active = True AND pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, host=host, port=port)
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'elo': item.elo if item.elo else '', 
                       'ranking': item.ranking if item.ranking else '', 
                       'level': item.level if item.level else '', 
                       'country_id': item.country_id if item.country_id else '', 
                       'country': item.country_name if item.country_name else '', 
                       'city_id': item.city_id if item.city_id else '', 
                       'city_name': item.city_name if item.city_name else '',
                       'receive_notifications': item.receive_notifications,
                       'lst_users': get_lst_users_team_profile(item.profile_id, single_profile_id=single_profile_id, db=db)}
    
    if not result.data:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    return result

def get_one_default_user_profile(request: Request, id: str, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
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
                       'photo': get_url_avatar(item.profile_id, item.photo, host=host, port=port),
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

def get_lst_users_team_profile(profile_id: str, single_profile_id: str, db: Session): 
    
    lst_data = []
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    str_query = "Select puse.single_profile_id profile_id, pmem.name, pmem.photo, pmem.city_id, is_principal, " +\
        "city.name as city_name, city.country_id, pa.name as country_name " +\
        "FROM enterprise.profile_users puse " +\
        "JOIN enterprise.profile_member pmem ON pmem.id = puse.single_profile_id " +\
        "left join resources.city city ON city.id = pmem.city_id " +\
        "left join resources.country pa ON pa.id = city.country_id " +\
        "Where pmem.is_active = True AND profile_id='" + profile_id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        # migue volvio a pedir que se incluyera
        # if item.profile_id == single_profile_id:
        #     continue
        
        lst_data.append({'profile_id': item.profile_id, 'name': item.name, 
                         'is_principal': item.is_principal,
                         'photo': get_url_avatar(item.profile_id, item.photo, host=host, port=port),
                         'country_id': item.country_id if item.country_id else '', 
                         'country': item.country_name if item.country_name else '', 
                         'city_id': item.city_id if item.city_id else '', 
                         'city_name': item.city_name if item.city_name else ''})
        
    return lst_data

def get_lst_users_pair_profile(profile_id: str, single_profile_id: str, db: Session): 
    
    dict_data = {}
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
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
                     'photo': get_url_avatar(item.profile_id, item.photo, host=host, port=port),
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
    
    result = ResultObject() 
    result.data = []
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    try:
        str_profile = "SELECT pus.username FROM enterprise.profile_member pme " +\
            "INNER JOIN enterprise.profile_users pus ON pus.profile_id = pme.id " +\
            "where pme.is_active = True AND pme.id = '" + profile_id + "' "
        user_name = db.execute(str_profile).scalar()
        if user_name:
            str_profile = "SELECT DISTINCT pme.id as profile_id, profile_type, prot.description, " +\
                "pme.name, pme.photo, pme.city_id, city.country_id, pa.name as country_name, " +\
                "city.name as city_name, pme.name, pme.email, pme.photo " +\
                "FROM enterprise.profile_member pme " +\
                "INNER JOIN enterprise.profile_users pus ON pus.profile_id = pme.id " +\
                "INNER JOIN enterprise.profile_type prot ON prot.name = pme.profile_type " +\
                "left join resources.city city ON city.id = pme.city_id " +\
                "left join resources.country pa ON pa.id = city.country_id " +\
                "where pme.is_active = True AND pus.username = '" + user_name + "' AND pme.id != '" + profile_id + "' "
            lst_data =  db.execute(str_profile)
            for item in lst_data:
                result.data.append({'profile_id': item.profile_id, 
                                    'profile_name': item.profile_type,
                                    'profile_description': item.description,
                                    'name': item.name,
                                    'email': item.email,
                                    'photo': get_url_avatar(item.profile_id, item.photo, host=host, port=port),
                                    'country_id': item.country_id if item.country_id else '', 
                                    'country': item.country_name if item.country_name else '', 
                                    'city_id': item.city_id if item.city_id else '', 
                                    'city_name': item.city_name if item.city_name else ''})  
     
        return result
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.imposible_delete"))

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
        
        result.data = get_url_avatar(db_single_profile.id, db_member_profile.photo)
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
    
    if defaultuserprofile['first_name'] and one_user.first_name != defaultuserprofile['first_name']:
        one_user.first_name = defaultuserprofile['first_name']
        
    if defaultuserprofile['last_name'] and one_user.last_name != defaultuserprofile['last_name']:
        one_user.last_name = defaultuserprofile['last_name']
        
    db_default_profile.name = defaultuserprofile['first_name'] + ' ' + defaultuserprofile['last_name'] if defaultuserprofile['last_name'] else one_user.last_name
    
    if defaultuserprofile['email'] and one_user.email != defaultuserprofile['email']:
        one_user.email = defaultuserprofile['email']
        db_default_profile.email = defaultuserprofile['email']
    
    if defaultuserprofile['phone'] and one_user.phone != defaultuserprofile['phone']:
        one_user.phone = defaultuserprofile['phone']
    
    if defaultuserprofile['city_id'] and db_default_profile_user.city_id != defaultuserprofile['city_id']:
        one_city = get_city_by_id(defaultuserprofile['city_id'], db=db)
        if not one_city:
            raise HTTPException(status_code=404, detail=_(locale, "city.not_found"))
        db_default_profile.city_id = defaultuserprofile['city_id']
        db_default_profile_user.city_id = defaultuserprofile['city_id']
        one_user.country_id = one_city.country_id
        
    if defaultuserprofile['sex'] and db_default_profile_user.sex != defaultuserprofile['sex']:
        db_default_profile_user.sex = defaultuserprofile['sex']
        
    if defaultuserprofile['birthdate'] and db_default_profile_user.birthdate != defaultuserprofile['birthdate']:
        db_default_profile_user.birthdate = defaultuserprofile['birthdate']
        
    if defaultuserprofile['alias'] and db_default_profile_user.alias != defaultuserprofile['alias']:
        db_default_profile_user.alias = defaultuserprofile['alias']
        
    if defaultuserprofile['job'] and db_default_profile_user.job != defaultuserprofile['job']:
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
        
        image_domino="public/profile/user-vector.jpg"
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
                   receive_notifications: bool):
    
    if profile_member.name != name:
        profile_member.name = name
        
    if profile_member.email != email:
        profile_member.email = email
        
    if profile_member.city_id != city_id:
        profile_member.city_id = city_id
        
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
        
        image_domino="public/profile/user-vector.jpg"
        filename = str(profile_member.id) + ".jpg"
        image_destiny = "public/profile/" + str(profile_member.id) + "/" + str(filename)
    
        copy_image(image_domino, image_destiny)
        profile_member.photo = filename
        
    return True
        
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
    
#endregion