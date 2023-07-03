from fastapi import HTTPException, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from domino.services.utils import upfile, create_dir, del_image, get_ext_at_file, remove_dir, copy_image

from domino.app import _

from domino.models.userprofile import ProfileMember, ProfileUsers, SingleProfile, DefaultUserProfile

def new_profile(profile_type, id, user_id, username, name, email, city_id, receive_notifications, is_ready, is_principal,
                entity_type, created_by, updated_by, file: File): 
    
    one_profile = ProfileMember(id=id, name=name, email=email, profile_type=profile_type.name, 
                                city_id=city_id, photo=file.filename if file else None, 
                                receive_notifications=receive_notifications, 
                                is_active=True, is_ready=is_ready, 
                                created_by=created_by, updated_by=updated_by)
    
    one_user_member = ProfileUsers(profile_id=id, username=username, is_principal=is_principal, created_by=created_by)
    one_profile.profile_users.append(one_user_member)  
    
    path = create_dir(entity_type=entity_type, user_id=str(user_id), entity_id=id)
    
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
        
    return one_profile

def new_profile_default_user(profile_type, id, user_id, username, name, email, city_id, receive_notifications, 
                             created_by, updated_by, sex, birthdate, alias, job, file: File): 
    
    one_profile = new_profile(profile_type, id, user_id, username, name, email, city_id, receive_notifications, 
                              True, True, "USERPROFILE", created_by, updated_by, file)
    new_default_user = DefaultUserProfile(profile_id=id, sex=sex, birthdate=birthdate,
                                          alias=alias, job=job, city_id=city_id, updated_by=updated_by)
    
    one_profile.profile_default_user.append(new_default_user)
    
    return one_profile