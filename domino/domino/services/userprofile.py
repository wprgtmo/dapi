import math
import uuid

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
from domino.services.utils import upfile, create_dir, del_image, get_ext_at_file, remove_dir, copy_image

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
                              True, True, "USERPROFILE", currentUser['username'], currentUser['username'], file)
    
    one_single_player = SingleProfile(profile_id=id, elo=0, ranking=None, updated_by=currentUser['username'])
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
                                   created_by=currentUser['username'])
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
    
    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, currentUser['user_id'], currentUser['username'], pairprofile['name'], 
                              pairprofile['email'], pairprofile['city_id'], pairprofile['receive_notifications'], 
                              True, True, "USERPROFILE", currentUser['username'], currentUser['username'], file)
    
    one_pair_player = PairProfile(profile_id=id, elo=0, level=pairprofile['level'], updated_by=currentUser['username'])
    one_profile.profile_pair_player.append(one_pair_player)
    
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
    
    id = str(uuid.uuid4())
    one_profile = new_profile(profile_type, id, currentUser['user_id'], currentUser['username'], teamprofile['name'], 
                              teamprofile['email'], teamprofile['city_id'], teamprofile['receive_notifications'], 
                              True, True, "USERPROFILE", currentUser['username'], currentUser['username'], file)
    
    one_team_player = TeamProfile(profile_id=id, elo=0, level=teamprofile['level'], updated_by=currentUser['username'])
    one_profile.profile_team_player.append(one_team_player)
    
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

def get_one_default_user(id: str, db: Session):  
    return db.query(DefaultUserProfile).filter(DefaultUserProfile.profile_id == id).first()

def get_one_referee_profile(id: str, db: Session):  
    return db.query(RefereeProfile).filter(RefereeProfile.profile_id == id).first()

def get_one_single_profile(id: str, db: Session):  
    return db.query(SingleProfile).filter(SingleProfile.profile_id == id).first()

def get_one_pair_profile(id: str, db: Session):  
    return db.query(PairProfile).filter(PairProfile.profile_id == id).first()

def get_one_team_profile(id: str, db: Session):  
    return db.query(TeamProfile).filter(TeamProfile.profile_id == id).first()

def get_one_single_profile(request: Request, id: str, db: Session): 
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_single_player sing ON sing.profile_id = pro.id " +\
        "Where pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, host=host, port=port)
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'city_id': item.city_id, 'receive_notifications': item.receive_notifications}
    
    return result

def get_one_referee_profile(request: Request, id: str, db: Session): 
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_referee sing ON sing.profile_id = pro.id " +\
        "Where pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, host=host, port=port)
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'city_id': item.city_id, 'receive_notifications': item.receive_notifications}
    
    return result

def get_one_pair_profile(request: Request, id: str, db: Session): 
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_pair_player sing ON sing.profile_id = pro.id " +\
        "Where pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, host=host, port=port)
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'city_id': item.city_id, 'receive_notifications': item.receive_notifications}
    
    return result

def get_one_team_profile(request: Request, id: str, db: Session): 
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_team_player sing ON sing.profile_id = pro.id " +\
        "Where pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = get_url_avatar(item.profile_id, item.photo, host=host, port=port)
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'city_id': item.city_id, 'receive_notifications': item.receive_notifications}
    
    return result

def get_one_default_user_profile(request: Request, id: str, db: Session): 
    
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
        "Where pro.id='" + id + "' "
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
        
    return result
    
def get_one_profile_id(id: str, db: Session): 
    str_query = "Select pro.id FROM enterprise.profile_member pro join enterprise.profile_users us ON us.profile_id = pro.id " +\
        "Where pro.id='" + id + "' "
        
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
    
    try:
        str_profile = "SELECT pus.username FROM enterprise.profile_member pme " +\
            "INNER JOIN enterprise.profile_users pus ON pus.profile_id = pme.id " +\
            "where pme.id = '" + profile_id + "' "
        user_name = db.execute(str_profile).scalar()
        if user_name:
            str_profile = "SELECT DISTINCT pme.id as profile_id, profile_type, prot.description " +\
                "FROM enterprise.profile_member pme " +\
                "INNER JOIN enterprise.profile_users pus ON pus.profile_id = pme.id " +\
                "INNER JOIN enterprise.profile_type prot ON prot.name = pme.profile_type " +\
                "where pus.username = '" + user_name + "' AND pme.id != '" + profile_id + "' "
            lst_data =  db.execute(str_profile)
            for item in lst_data:
                result.data.append({'profile_id': item.profile_id, 
                                    'name': item.profile_type,
                                    'description': item.description})  
     
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
    
    db_single_profile = get_one(id, db=db)
    if not db_single_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    update_profile(db_single_profile, file, currentUser, singleprofile['name'], singleprofile['email'], singleprofile['city_id'], 
                   singleprofile['receive_notifications'])
        
    try:
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
    
    db_profile = get_one(id, db=db)
    if not db_pair_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    update_profile(db_profile, file, currentUser, pairprofile['name'], pairprofile['email'], pairprofile['city_id'], 
                   pairprofile['receive_notifications'])
    
    db_pair_profile = get_one_pair_profile(db_profile.id, db=db)
    db_pair_profile.level = pairprofile['level']
        
    try:
        db.add(db_profile)
        db.add(db_pair_profile)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        print(e.code)
        if e.code == "gkpj":
            raise HTTPException(status_code=400, detail=_(locale, "userprofile.already_exist"))
        
def update_one_team_profile(request: Request, id: str, teamprofile: TeamProfileCreated, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_profile = get_one(id, db=db)
    if not db_team_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    update_profile(db_profile, file, currentUser, teamprofile['name'], teamprofile['email'], teamprofile['city_id'], 
                   teamprofile['receive_notifications'])
    
    db_team_profile = get_one_team_profile(db_profile.id, db=db)
    db_team_profile.level = teamprofile['level']
        
    try:
        db.add(db_profile)
        db.add(db_team_profile)
        db.commit()
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
    if not db_referee_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    update_profile(db_profile, file, currentUser, refereeprofile['name'], refereeprofile['email'], refereeprofile['city_id'], 
                   refereeprofile['receive_notifications'])
    
    db_referee_profile = get_one_referee_profile(db_profile.id, db=db)
    db_referee_profile.level = refereeprofile['level']
        
    try:
        db.add(db_profile)
        db.add(db_referee_profile)
        db.commit()
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