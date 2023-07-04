import math
import uuid

from datetime import datetime

from domino.config.config import settings
from fastapi import HTTPException, Request, File
from unicodedata import name
from domino.functions_jwt import get_current_user
from fastapi import HTTPException
from domino.models.userprofile import ProfileMember, ProfileUsers, SingleProfile, DefaultUserProfile
from domino.schemas.userprofile import SingleProfileCreated, DefaultUserProfileBase
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

def new_profile_default_user(request: Request, defaultuserprofile: DefaultUserProfileBase, file: File, db: Session): 
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    profile_type = get_profile_type_by_name("USER", db=db)
    if not profile_type:
        raise HTTPException(status_code=400, detail=_(locale, "profiletype.not_found"))
    
    # si ya tengo perfil no permitir crear otro.
    exist_profile_id = get_one_profile_by_user(currentUser['username'], "USER", db=db)
    if exist_profile_id:
        raise  HTTPException(status_code=400, detail=_(locale, "userprofile.existprofile"))
    
    id = str(uuid.uuid4())
    
    # buscar el usuario para coger sus datos
    username = defaultuserprofile.username if defaultuserprofile.username else currentUser['username']
    
    one_user = get_one_by_username(username=username, db=db)
    
    name = one_user.first_name + ' ' + defaultuserprofile['last_name'] if defaultuserprofile['last_name'] else one_user.last_name
    one_profile = ProfileMember(id=id, name=name, email=defaultuserprofile['email'] if defaultuserprofile['email'] else None, 
                                profile_type=profile_type.name, 
                                city_id=defaultuserprofile['city_id'] if defaultuserprofile['city_id'] else None, 
                                photo=file.filename if file else None, 
                                receive_notifications=defaultuserprofile['receive_notifications'], 
                                is_active=True, is_ready=True, 
                                created_by=currentUser['username'], updated_by=currentUser['username'])
    
    one_user_member = ProfileUsers(profile_id=id, username=username, is_principal=True, 
                                   created_by=currentUser['username'])
    one_profile.profile_users.append(one_user_member)  
    
    one_default_user = DefaultUserProfile(profile_id=id, sex=defaultuserprofile.sex, birthdate=defaultuserprofile.birthdate,
                                          alias=defaultuserprofile.alias, job=defaultuserprofile.job,
                                          city_id=defaultuserprofile.city_id, is_active=True,
                                          updated_by=currentUser['username'])
    
    one_profile.profile_default_user.append(one_default_user)
    
    path = create_dir(entity_type="USERPROFILE", user_id=str(currentUser['user_id']), entity_id=id)
    
    # si los datos de el como usuario no estan completo ponerle el que dice en el perfil.
    
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
    
def get_one(id: str, db: Session):  
    return db.query(ProfileMember).filter(ProfileMember.id == id).first()

def get_one_default_user(id: str, db: Session):  
    return db.query(DefaultUserProfile).filter(DefaultUserProfile.profile_id == id).first()

def get_one_single_profile(request: Request, id: str, db: Session): 
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    str_query = "Select pro.id profile_id, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "Where pro.id='" + id + "' "
    res_profile=db.execute(str_query)
    
    for item in res_profile:
        photo = "http://" + host + ":" + port + "/public/profile/" + str(item.profile_id) + "/" + item.photo 
        
        result.data = {'id': item.profile_id, 'name': item.name, 'email': item.email,
                       'profile_type_name': item.profile_type_name, 
                       'profile_type_description': item.profile_type_description, 'photo': photo,
                       'city_id': item.city_id, 'receive_notifications': item.receive_notifications}
    
    return result

def get_one_default_user_profile(request: Request, id: str, db: Session): 
    
    result = ResultObject() 
    
    host = str(settings.server_uri)
    port = str(int(settings.server_port))
    
    str_query = "Select pro.id profile_id, username, pro.name, pro.email, pro.city_id, pro.photo, pro.receive_notifications, " +\
        "eve.name as profile_type_name, eve.description as profile_type_description, " +\
        "us.first_name, us.last_name, us.phone, us.is_active, us.country_id, " +\
        "def.job, def.sex, def.birthdate, def.alias, pa.name as country_name, " +\
        "city.id as city_id, city.name as city_name " +\
        "FROM enterprise.profile_member pro " +\
        "inner join enterprise.profile_type eve ON eve.name = pro.profile_type " +\
        "inner join enterprise.profile_default_user def ON def.profile_id = pro.id " +\
        "inner join enterprise.users us ON us.id = pro.id " +\
        "left join resources.country pa ON pa.id = us.country_id " +\
        "left join resources.city city ON city.id = pro.city_id " +\
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
        
def update_one_single_profile(request: Request, id: str, singleprofile: SingleProfileCreated, file: File, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_single_profile = get_one(id, db=db)
    if not db_single_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    if singleprofile['name'] and db_single_profile.name != singleprofile['name']:
        db_single_profile.name = singleprofile['name']
        
    if singleprofile['email'] and db_single_profile.email != singleprofile['email']:
        db_single_profile.email = singleprofile['email']
        
    if singleprofile['city_id'] and db_single_profile.city_id != singleprofile['city_id']:
        db_single_profile.city_id = singleprofile['city_id']
        
    db_single_profile.receive_notifications = singleprofile['receive_notifications']
    
    path = create_dir(entity_type="USERPROFILE", user_id=str(currentUser['user_id']), entity_id=db_single_profile.id)    
    if file:
        ext = get_ext_at_file(file.filename)
        current_image = db_single_profile.photo
        file.filename = str(uuid.uuid4()) + "." + ext if ext else str(uuid.uuid4())
        db_single_profile.photo = file.filename
        path_del = "/public/profile/" + str(db_single_profile.id) + "/"
        try:
            del_image(path=path_del, name=str(current_image))
        except:
            pass
        upfile(file=file, path=path)
        
    else:
        if not db_single_profile.photo:
            image_domino="public/profile/user-vector.jpg"
            filename = str(currentUser['user_id']) + ".jpg"
            image_destiny = path + "/" + str(filename)
        
            copy_image(image_domino, image_destiny)
            db_single_profile.photo = filename
            
    try:
        db.add(db_single_profile)
        db.commit()
        db.refresh(db_single_profile)
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
    if avatar:
        ext = get_ext_at_file(avatar.filename)
        current_image = db_default_profile.photo
        avatar.filename = str(uuid.uuid4()) + "." + ext if ext else str(uuid.uuid4())
        db_default_profile.photo = avatar.filename
        path_del = "/public/profile/" + str(one_user.id) + "/" 
        try:
            del_image(path=path_del, name=str(current_image))
        except:
            pass
        upfile(file=avatar, path=path)
        
    else:
        if not db_default_profile.photo:
            image_domino="public/profile/user-vector.jpg"
            filename = str(db_default_profile.id) + ".jpg"
            image_destiny = "public/profile/" + str(db_default_profile.id) + "/" + str(filename)
        
            copy_image(image_domino, image_destiny)
            db_default_profile.photo = filename
    
    db_default_profile.updated_by = currentUser['username']
    db_default_profile.updated_date = datetime.now()
    
    one_user.updated_by = currentUser['username']
    one_user.updated_date = datetime.now()
        
    # try:
    db.add(db_default_profile)
    db.add(one_user)
    db.add(db_default_profile_user)
    db.commit()
    if avatar:
        filename = avatar.filename
        
    result.data = get_url_avatar(db_default_profile.id, filename)
    return result
    # except (Exception, SQLAlchemyError) as e:
    #     if e and e.code == "gkpj":
    #         raise HTTPException(status_code=400, detail=_(locale, "users.already_exist"))    
         
def delete_one_single_profile(request: Request, id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    try:
        db_profile = db.query(ProfileMember).filter(ProfileMember.id == id).first()
        if db_profile:
            db_profile.is_active = False
            db_profile.updated_by = currentUser['username']
            db_profile.updated_date = datetime.now()
            db.commit()
            
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
                
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.imposible_delete"))
    
def delete_one_default_profile(request: Request, id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    try:
        db_profile = db.query(ProfileMember).filter(ProfileMember.id == id).first()
        if db_profile:
            db_user = get_one_user_by_id(user_id=id, db=db)
            if not db_user:
                raise HTTPException(status_code=400, detail=_(locale, "user.not_found"))
            
            db_profile.is_active = False
            db_profile.updated_by = currentUser['username']
            db_profile.updated_date = datetime.now()
            
            db_user.is_active = False
            db_user.updated_by = currentUser['username']
            db_user.updated_date = datetime.now()
            
            db.commit()
            
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
                
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "userprofile.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.imposible_delete"))

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
            str_profile = "SELECT DISTINCT prot.id as profile_type_id, profile_type, prot.description " +\
                "FROM enterprise.profile_member pme " +\
                "INNER JOIN enterprise.profile_users pus ON pus.profile_id = pme.id " +\
                "INNER JOIN enterprise.profile_type prot ON prot.name = pme.profile_type " +\
                "where pus.username = '" + user_name + "' AND pme.id != '" + profile_id + "' "
            lst_data =  db.execute(str_profile)
            for item in lst_data:
                result.data.append({'id': item.profile_type_id, 
                                    'name': item.profile_type,
                                    'description': item.description})  
     
        return result
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "userprofile.imposible_delete"))