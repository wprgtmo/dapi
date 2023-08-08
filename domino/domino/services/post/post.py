import math
import time
import uuid

from domino.config.config import settings
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, File
from typing import List
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user

from domino.app import _

from domino.models.post.post import Post, PostLikes, PostComments, PostFiles, CommentComments, CommentLikes
from domino.schemas.post.post import PostBase, PostUpdated, PostCreated
from domino.schemas.post.postelement import PostFileCreate, PostLikeCreate, PostCommentCreate, CommentCommentCreate, CommentLikeCreate
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file
from domino.services.enterprise.userprofile import get_one as get_one_profile, get_single_profile_id_for_profile_by_user

from domino.services.enterprise.users import get_one_by_username, get_url_avatar
            
def get_all(request:Request, page: int, per_page: int, criteria_key: str, criteria_value: str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    str_count = "Select count(*) FROM post.post po LEFT JOIN enterprise.users us ON po.created_by = us.username "
    str_query = "Select po.id, summary, us.first_name || ' ' || us.last_name as full_name, po.created_date, us.photo, " +\
        "us.id as user_id, po.allow_comment, po.show_count_like " +\
        "FROM post.post po LEFT JOIN enterprise.users us ON po.created_by = us.username "

    dict_query = {'summary': " WHERE summary ilike '%" + criteria_value + "%'",
                  'created_by': " WHERE created_by = '" + criteria_value + "'"
                  }
    
    if criteria_key and criteria_key not in dict_query:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    if page and page > 0 and not per_page:
        raise HTTPException(status_code=404, detail=_(locale, "commun.invalid_param"))
    
    str_count += dict_query[criteria_key] if criteria_value else "" 
    str_query += dict_query[criteria_key] if criteria_value else "" 
    
    result = get_result_count(page=page, per_page=per_page, str_count=str_count, db=db)
    str_query += " ORDER BY created_date DESC " 
    
    if page != 0:
        str_query += "LIMIT " + str(per_page) + " OFFSET " + str(page*per_page-per_page)
    
    lst_data = db.execute(str_query)
    current_date = datetime.now()
    result.data = [create_dict_row(item, current_date, db=db) for item in lst_data]
    
    return result

def get_list_post(request:Request, profile_id:str, db: Session):  
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    current_date = datetime.now()
    date_find = datetime.now() - timedelta(days=40)
    currentUser = get_current_user(request)
    
    # si el perfil es de usuario, mostrar todos los post creado por sus perfile. 
    # si estoy en otro perfil, solo los de ese perfil y mis seguidores.
    
    db_profile = get_one_profile(id=profile_id, db=db)
    if not db_profile:
        raise HTTPException(status_code=400, detail=_(locale, "userprofile.not_found"))
    
    str_query = "Select po.id, summary, pmem.name as full_name, po.created_date, pmem.photo, " +\
        "us.id as user_id, pmem.id as profile_id, po.allow_comment, po.show_count_like " +\
        "FROM post.post po " +\
        "JOIN enterprise.profile_member pmem ON pmem.id = po.profile_id " +\
        "JOIN enterprise.users us ON po.created_by = us.username " +\
        "WHERE po.is_active=True AND po.updated_date >= '" + date_find.strftime('%Y-%m-%d') + "' " +\
        "AND (po.profile_id = '" + profile_id + "' or po.created_by = 'domino' or " 
    
    if  db_profile.profile_type == 'USER':
        str_query += "po.created_by = '" + currentUser['username'] + "' or "  
        
    str_query += "po.profile_id IN (SELECT profile_follow_id FROM enterprise.profile_followers " +\
        "where profile_id = '" + profile_id + "'))"
  
    str_query += " ORDER BY created_date DESC " 
    
    lst_data = db.execute(str_query)
    host=str(settings.server_uri)
    port=str(int(settings.server_port))
  
    result.data = [create_dict_row(item, current_date, profile_id, db=db, host=host, port=port) for item in lst_data]
    
    return result

def create_dict_row(item, current_date, profile_id, db: Session, host='', port=''):
    
    amount_like, amount_comments = get_amount_element_of_post(item['id'], db=db)
    return {'id': item['id'], 
            'user_id': item['user_id'],
            'profile_id': item['profile_id'],
            'name': item['full_name'],
            'avatar': get_url_avatar(item['profile_id'], item['photo'], host, port) if item['photo'] else "", 
            'elapsed': calculate_time(current_date, item['created_date']), 
            'comment': item['summary'] if item['summary'] else "",
            'amountLike': amount_like, 'amountComment': amount_comments, 
            'comments': get_comments_of_post(item['id'], current_date, db=db, host=host, port=port),
            'photos': get_files_of_post(item['id'], db=db, host=host, port=port),
            'like': verify_likes(str(item['id']), profile_id, db=db),
            "allowComment": item['allow_comment'], "showCountLike": item['show_count_like']
            }

def calculate_time(current_date, star_date):
    
    diferencia = current_date - star_date
    if diferencia.days > 0:
        return str(diferencia.days) + ' d'
    else:
        hours = diferencia.seconds // 3600
        if hours > 0:
            return str(hours) + ' h'
        else:
            minutes = diferencia.seconds // 60
            if minutes > 0:
                return str(minutes) + ' min'
            else:
                return str(diferencia.seconds) + ' seg'

def verify_likes(post_id, profile_id, db: Session):
    
    str_count = "SELECT count(id) FROM post.post_likes Where post_id = '" +\
        post_id + "' and profile_id = '" + profile_id + "'"
    
    exist_like = db.execute(str_count).scalar()   
    
    return True if exist_like else False
 
def get_amount_element_of_post(post_id, db: Session):
    
    str_count = "SELECT count(*) FROM "
    str_where = "where post_id = '" + post_id + "' "
    
    str_likes = str_count + "post.post_likes " + str_where 
    str_comments = str_count + "post.post_comments " + str_where 
    
    amount_like = db.execute(str_likes).scalar()
    amount_comments = db.execute(str_comments).scalar()
    
    return amount_like, amount_comments

def get_comments_of_post(post_id: str, current_date: datetime, db: Session, host='', port=''):
    
    # no devolver datos del usuario sino del profile...
    # str_comments = "SELECT po.id, us.first_name || ' ' || us.last_name as full_name, pmem.photo, summary, " +\
        
    str_comments = "SELECT po.id, pmem.name full_name, pmem.photo, summary, " +\
        "po.created_date, us.id as user_id, us.username, po.profile_id FROM post.post_comments po " +\
        "JOIN enterprise.profile_member pmem ON pmem.id = po.profile_id " +\
        "JOIN enterprise.users us ON po.created_by = us.username " +\
        "WHERE post_id = '" + post_id + "' ORDER BY po.created_date DESC LIMIT 3 "
    
    lst_comments = db.execute(str_comments)
    lst_result = []
    for item_comment in lst_comments:
        one_like_comment = get_one_like_at_comment(item_comment['id'], item_comment['username'], db=db)
        lst_result.append({'id': item_comment['id'], 'name': item_comment['full_name'], 
                           'profile_id': item_comment['profile_id'],
                           'user_id': item_comment['user_id'],
                           'avatar': get_url_avatar(item_comment['profile_id'], item_comment['photo'], host, port) if item_comment['photo'] else "",
                           'comment': item_comment['summary'] if item_comment['summary'] else "", 
                           'comments': get_comments_of_comment(item_comment['id'], current_date, db=db),
                           'like': True if one_like_comment else False,
                           'elapsed': calculate_time(current_date, item_comment['created_date'])})
    
    return lst_result

def get_comments_of_comment(comment_id: str, current_date: datetime, db: Session, host='', port=''):
    
    # str_comments = "SELECT co.id, us.first_name || ' ' || us.last_name as full_name, pmem.photo, summary,co.created_by, " +\
        
    str_comments = "SELECT co.id, pmem.name full_name, pmem.photo, summary,co.created_by, " +\
        "co.created_date, us.id as user_id, us.username, co.profile_id FROM post.comment_comments co " +\
        "JOIN enterprise.profile_member pmem ON pmem.id = co.profile_id " +\
        "JOIN enterprise.users us ON co.created_by = us.username " +\
        "WHERE comment_id = '" + comment_id + "' ORDER BY co.created_date DESC LIMIT 3 "
    lst_comments = db.execute(str_comments)
 
    lst_result = []
    for item_comment in lst_comments:
        one_like_comment = get_one_like_at_comment(item_comment['id'], item_comment['username'], db=db)
        lst_result.append({'id': item_comment['id'], 'name': item_comment['full_name'], 
                           'profile_id': item_comment['profile_id'],
                           'user_id': item_comment['user_id'],
                           'avatar': get_url_avatar(item_comment['profile_id'], item_comment['photo'], host, port) if item_comment['photo'] else "",
                           'comment': item_comment['summary'] if item_comment['summary'] else "", 
                           'like': True if one_like_comment else False,
                           'elapsed': calculate_time(current_date, item_comment['created_date'])})
    
    return lst_result

def get_files_of_post(post_id: str, db: Session, host='', port=''):
    
    str_files = "SELECT id, path FROM post.post_files WHERE post_id = '" + post_id + "' "
    lst_files = db.execute(str_files)
 
    lst_result = []
    if host:
        path = "http://" + host + ":" + port + "/api/pictures/post/" #+ str(item['user_id']) + "/" + item['id'] + "/" + item['image']
    
    for item_file in lst_files:
        path_file = path + post_id + "/" + item_file['path']
        lst_result.append({'file_id': item_file['id'], 'path': path_file, 'type': get_ext_type(item_file['path'])})
    
    return lst_result

def get_one(post_id: str, db: Session):  
    return db.query(Post).filter(Post.id == post_id).first()

def get_one_postcomment(comment_id: str, db: Session):  
    return db.query(PostComments).filter(PostComments.id == comment_id).first()

def get_one_like_by_user(post_id: str, user_name:str, db: Session): 
    return db.query(PostLikes).filter(PostLikes.post_id == post_id, PostLikes.created_by == user_name).first()

def get_one_like_by_profile(post_id: str, profile_id:str, db: Session): 
    return db.query(PostLikes).filter(PostLikes.post_id == post_id, PostLikes.profile_id == profile_id).first()

def get_one_like_at_comment(post_comment_id: str, user_name:str, db: Session): 
    return db.query(CommentLikes).filter(CommentLikes.comment_id == post_comment_id, CommentLikes.created_by == user_name).first()

def get_one_like_at_comment_by_profile(post_comment_id: str, profile_id:str, db: Session): 
    return db.query(CommentLikes).filter(CommentLikes.comment_id == post_comment_id, CommentLikes.profile_id == profile_id).first()

def get_one_by_id(post_id: str, db: Session): 
    result = ResultObject()  
    host=str(settings.server_uri)
    port=str(int(settings.server_port))
    
    result.data = db.query(Post).filter(Post.id == post_id).first()
    result.data.photos = get_files_of_post(post_id, db=db, host=host, port=port)
    return result

def new(request, db: Session, profile_id: str, post: PostCreated, files: List[File]):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    id = str(uuid.uuid4())
    
    db_post = Post(id=id, summary=post['summary'], created_by=currentUser['username'], updated_by=currentUser['username'],
                   is_active=True, allow_comment=True, show_count_like=True, profile_id=profile_id)
    
    if files:
        path = create_dir(entity_type="POST", user_id=str(currentUser['user_id']), entity_id=str(id))
        
        for item_file in files:
            file_id = str(uuid.uuid4())
            ext = get_ext_at_file(item_file.filename)
            item_file.filename = str(file_id) + "." + ext
        
            post_file = PostFiles(id=file_id, path=item_file.filename)
            db_post.files.append(post_file)
            upfile(file=item_file, path=path)
            
    try:
        db.add(db_post)
        db.commit()
        result.data = {'post_id': id}
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_post")               
        raise HTTPException(status_code=403, detail=msg)

def delete(request: Request, post_id: str, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    try:
        db_post = db.query(Post).filter(Post.id == post_id).first()
        if db_post:
            db_post.is_active = False
            db_post.updated_by = currentUser['username']
            db_post.updated_date = datetime.now()
            # borrar las imagenes
            
            for item_file in db_post.files:
                user_created = get_one_by_username(db_post.created_by, db=db)
                path = "/public/post/" + str(user_created.id) + "/" + str(db_post.id)
                try:
                    del_image(path=path, name=str(item_file.path))
                except:
                    print('No encontre, dio ERROR')
                    pass
            
            db.commit()
            return result
        else:
            raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
        
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail=_(locale, "post.imposible_delete"))
 
def update(request: Request, post_id: str, post: PostCreated, files: List[File], db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request) 
       
    db_post = db.query(Post).filter(Post.id == post_id).first()
    
    if db_post:
    
        if db_post.summary != post.summary:    
            db_post.summary = post.summary
        
        db_post.updated_by = currentUser['username']
        db_post.updated_date = datetime.now()
        
        if files:
            path = create_dir(entity_type="POST", user_id=str(currentUser['user_id']), entity_id=str(db_post.id))
            print(path)
            for item_file in files:
                file_id = str(uuid.uuid4())
                ext = get_ext_at_file(item_file.filename)
                item_file.filename = str(file_id) + "." + ext
            
                post_file = PostFiles(id=file_id, path=item_file.filename)
                db_post.files.append(post_file)
                upfile(file=item_file, path=path)
                
        try:
            db.add(db_post)
            db.commit()
            db.refresh(db_post)
            return result
        except (Exception, SQLAlchemyError) as e:
            print(e.code)
            if e.code == "gkpj":
                raise HTTPException(status_code=400, detail=_(locale, "post.already_exist"))
            
    else:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))

def add_one_file(request, db: Session, postfile: PostFileCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_post = get_one(postfile.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    db_postfile = PostFiles(post_id=postfile.post_id, path=postfile.path, created_by=currentUser['username'])
    
    try:
        one_post.updated_by = currentUser['username']
        one_post.updated_date = datetime.now()
        
        db.add(db_postfile)
        db.commit()
        db.refresh(db_postfile)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_postimage")               
        raise HTTPException(status_code=403, detail=msg)
   
def remove_one_file(request: Request, db: Session, post_id: str, file_id: str):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    db_post_file = db.query(PostFiles).filter(PostFiles.id == file_id).first()
    if not db_post_file:
        raise HTTPException(status_code=404, detail=_(locale, "post.file_not_found"))
    
    try:
        db.delete(db_post_file)
        path_del = "public/post/" + post_id + "/"
        
        try:
            del_image(path=path_del, name=str(db_post_file.path))
        except:
            pass
            
        db.commit()
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_remove_postfile")               
        raise HTTPException(status_code=403, detail=msg)
    
def add_one_likes(request, profile_id: str, db: Session, postlike: PostLikeCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    # verifico si tiene, si es positivo se lo quito, sino tiene se lo pongo.
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_post = get_one(postlike.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    db_postlike = get_one_like_by_profile(postlike.post_id, profile_id, db=db)
    
    try:
        one_post.updated_by = currentUser['username']
        one_post.updated_date = datetime.now()
        
        if db_postlike:
            db.delete(db_postlike)
        else:
            db_postlike = PostLikes(post_id=postlike.post_id, created_by=currentUser['username'], profile_id=profile_id)
            db.add(db_postlike)
            
        db.commit()    
        return result
    
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_postlike")               
        raise HTTPException(status_code=403, detail=msg)

def update_one_allow_comment(request, db: Session, postlike: PostLikeCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    # verifico si tiene, si es positivo se lo quito, sino tiene se lo pongo.
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_post = get_one(postlike.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    try:
        
        one_post.allow_comment = False if one_post.allow_comment else True
        
        one_post.updated_by = currentUser['username']
        one_post.updated_date = datetime.now()
        
        db.commit()    
        return result
    
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_postallow_comment")               
        raise HTTPException(status_code=403, detail=msg)
    
def update_one_show_count_like(request, db: Session, postlike: PostLikeCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    # verifico si tiene, si es positivo se lo quito, sino tiene se lo pongo.
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_post = get_one(postlike.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    try:
        
        one_post.show_count_like = False if one_post.show_count_like else True
        
        one_post.updated_by = currentUser['username']
        one_post.updated_date = datetime.now()
        
        db.commit()    
        return result
    
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_postallow_comment")               
        raise HTTPException(status_code=403, detail=msg)
        
def add_one_comment(request, profile_id: str, db: Session, postcomment: PostCommentCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_post = get_one(postcomment.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    one_post.updated_by = currentUser['username']
    one_post.updated_date = datetime.now()
        
    db_postcomment = PostComments(post_id=postcomment.post_id, summary=postcomment.summary, created_by=currentUser['username'],
                                  profile_id=profile_id)
    
    try:
        db.add(db_postcomment)
        db.commit()
        db.refresh(db_postcomment)
        result.data = get_comments_of_post(postcomment.post_id, datetime.now(), db=db)
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_postcomment")               
        raise HTTPException(status_code=403, detail=msg)
    
def add_one_likes_at_comment(request, profile_id: str, db: Session, commentlike: CommentLikeCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_comment = get_one_postcomment(commentlike.comment_id, db=db)
    if not one_comment:
        raise HTTPException(status_code=404, detail=_(locale, "post.comment_not_found"))
    
    one_post = get_one(one_comment.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    db_commentlike = get_one_like_at_comment_by_profile(commentlike.comment_id, profile_id, db=db)
    
    try:
        one_post.updated_by = currentUser['username']
        one_post.updated_date = datetime.now()
        
        one_comment.updated_by = currentUser['username']
        one_comment.updated_date = datetime.now()
        
        if db_commentlike:
            db.delete(db_commentlike)
        else:
            db_commentlike = CommentLikes(comment_id=commentlike.comment_id, created_by=currentUser['username'],
                                          profile_id=profile_id)
            db.add(db_commentlike)
            
        db.commit()    
        return result
    
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_postlike")               
        raise HTTPException(status_code=403, detail=msg)
    
def add_one_comment_at_comment(request, profile_id: str, db: Session, commentcomment: CommentCommentCreate):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    currentUser = get_current_user(request)
    
    one_comment = get_one_postcomment(commentcomment.comment_id, db=db)
    if not one_comment:
        raise HTTPException(status_code=404, detail=_(locale, "post.comment_not_found"))
    
    one_post = get_one(one_comment.post_id, db=db)
    if not one_post:
        raise HTTPException(status_code=404, detail=_(locale, "post.not_found"))
    
    one_post.updated_by = currentUser['username']
    one_post.updated_date = datetime.now()
    
    db_comment_comment = CommentComments(comment_id=commentcomment.comment_id, summary=commentcomment.summary, 
                                         created_by=currentUser['username'], profile_id=profile_id)
    
    try:
        db.add(db_comment_comment)
        db.commit()
        db.refresh(db_comment_comment)
        result.data = db_comment_comment.dict()
        return result
    except (Exception, SQLAlchemyError, IntegrityError) as e:
        print(e)
        msg = _(locale, "post.error_new_commentcomment")               
        raise HTTPException(status_code=403, detail=msg)
    
def get_ext_type(path: str):
    
    dict_ext = {'bmp': 'image', 'gif': 'image', 'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'tif': 'image', 'tiff': 'image',
                'mp4': 'video', 'mov': 'video', 'wmv': 'video', 'avi': 'video', 'mkv': 'video', 'flv': 'video', 'webm': 'video', 'html5': 'video'} 
    
    path = path.lower()
    pos_ext = path.rfind('.')
   
    ext = dict_ext[path[pos_ext+1:]] if pos_ext > 0 else 'no type'

    return ext

