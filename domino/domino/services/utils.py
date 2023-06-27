
import math
import os
import shutil
from fastapi import FastAPI, Request, UploadFile, File
from os import getcwd, remove

# from fastapi import Request
from sqlalchemy.orm import Session
from fastapi import HTTPException
from domino.schemas.result_object import ResultObject, ResultData

def get_result_count(page: int, per_page: int, str_count: str, db: Session): 
    if page != 0:
        result = ResultData(page=page, per_page=per_page)  
        
        result.total = db.execute(str_count).scalar()
        result.total_pages=result.total/result.per_page if (result.total % result.per_page == 0) else math.trunc(result.total / result.per_page) + 1
    else:
        result = ResultObject()
        
    return result

def upfile(file: File, path: str):
    if not os.path.isdir(path):
        os.mkdir(path)
                
    path = path + "/" + file.filename
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return True

def create_dir(entity_type: str, user_id: str, entity_id: str):
    path = ""
    if not os.path.isdir("public"):
        os.mkdir("public")
        
    if entity_type == 'POST':
        if not os.path.isdir("public/post"):
            os.mkdir("public/post")
        path = "public/post/"
        
    elif entity_type == 'EVENT':
        if not os.path.isdir("public/events"):
            os.mkdir("public/events")
        path = "public/events/"
        
    elif entity_type == 'USER' or entity_type == 'USERPROFILE':
        if not os.path.isdir("public/profile"):
            os.mkdir("public/profile")
        path = "public/profile/"
        
    # elif entity_type == 'USERPROFILE':
    #     if not os.path.isdir("public/profile/player"):
    #         os.mkdir("public/profile/player")
    #     path = "public/profile/player/"
    
    if entity_type == 'EVENT' or entity_type == 'USER' or entity_type == 'USERPROFILE':
        path += str(user_id) 
        if not os.path.isdir(path):
            os.mkdir(path)
        path += "/"
    
    if entity_id:
        path += str(entity_id)
        if not os.path.isdir(path):
            os.mkdir(path)
        path += "/"
        
    return path

def remove_dir(path: str):
    os.rmdir(path)
    os.rmdir(getcwd() + path)
    return True

def copy_image(image_origen: str, image_destiny: str):
    if not os.path.exists(image_origen):
        raise HTTPException(status_code=400, detail="FileNotFoundError")
    
    shutil.copy(image_origen, image_destiny)
    return True

def del_image(path: str, name: str):
    try:
        remove(getcwd() + path + name)
        return True
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="FileNotFoundError")
    
def get_ext_at_file(filename: str):
    ext = ""
    if filename:
        pos = filename.find(".")
        if pos:
            ext = filename[pos+1:]
            
    return ext
