
import math
import shutil
from fastapi import FastAPI, Request, UploadFile, File

# from fastapi import Request
from sqlalchemy.orm import Session
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
    import os

    # path = "public/events"
    if not os.path.isdir(path):
        os.mkdir(path)
                
    path = path + "/" + file.filename
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return True

def create_dir(entity_type: str, user_id: str, entity_id: str):
    import os
    
    path = ""
    if not os.path.isdir("public"):
        os.mkdir("public")
        
    if entity_type == 'POST':
        if not os.path.isdir("public/post"):
            print('creando post')
            os.mkdir("public/post")
        path = "public/post/"
        
    elif entity_type == 'EVENT':
        if not os.path.isdir("public/events"):
            print('creando event')
            os.mkdir("public/events")
        path = "public/events/"
    
    path += str(user_id) 
    if not os.path.isdir(path):
        os.mkdir(path)
    
    path += "/" + str(entity_id)
    if not os.path.isdir(path):
        os.mkdir(path)
        
    path += "/"
    
    return path