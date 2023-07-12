from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from domino.schemas.post import PostBase, PostUpdated, PostCreated
from domino.schemas.postelement import PostLikeCreate, PostCommentCreate, PostFileCreate, CommentCommentCreate, CommentLikeCreate
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.post import get_all, new, get_one_by_id, delete, update, add_one_likes, add_one_comment, \
    add_one_file, remove_one_file, get_list_post, update_one_allow_comment, update_one_show_count_like
from starlette import status
from domino.auth_bearer import JWTBearer
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from os import getcwd, remove, path, stat
  
post_route = APIRouter(
    tags=["Post"],
    dependencies=[Depends(JWTBearer())]   
)

@post_route.get("/post/all/", response_model=Dict, summary="Obtain a list of Post.")
def get_post(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@post_route.get("/post", response_model=Dict, summary="Obtain a list of Post.")
def get_last_post(
    request: Request,
    db: Session = Depends(get_db)
):
    return get_list_post(request=request, db=db)

@post_route.get("/post/one/{id}", response_model=ResultObject, summary="Get a Post for your ID.")
def get_post_by_id(id: str, db: Session = Depends(get_db)):
    return get_one_by_id(post_id=id, db=db)

@post_route.post("/post", response_model=ResultObject, summary="Create a Post.")
def create_post(request:Request, post: PostCreated = Depends(), files: List[UploadFile] = [], db: Session = Depends(get_db)):
    return new(request=request, post=post.dict(), db=db, files=files)

@post_route.delete("/post/{id}", response_model=ResultObject, summary="Deactivate a Post by its ID.")
def delete_post(request:Request, id: str, db: Session = Depends(get_db)):
    return delete(request=request, post_id=str(id), db=db)
    
@post_route.put("/post/{id}", response_model=ResultObject, summary="Update a Post by its ID")
def update_post(request:Request, id: str, post: PostCreated = Depends(), files: List[UploadFile] = [], db: Session = Depends(get_db)):
    return update(request=request, db=db, post_id=str(id), post=post, files=files)

@post_route.post("/postlike", response_model=ResultObject, summary="Create a like at Post.")
def add_like(request:Request, postlike: PostLikeCreate, db: Session = Depends(get_db)):
    return add_one_likes(request=request, postlike=postlike, db=db)

@post_route.post("/allow_comment", response_model=ResultObject, summary="Update allow_comment property")
def update_allow_comment(request:Request, postlike: PostLikeCreate, db: Session = Depends(get_db)):
    return update_one_allow_comment(request=request, postlike=postlike, db=db)

@post_route.post("/show_count_like", response_model=ResultObject, summary="Update show_count_like property")
def update_show_count_like(request:Request, postlike: PostLikeCreate, db: Session = Depends(get_db)):
    return update_one_show_count_like(request=request, postlike=postlike, db=db)

@post_route.post("/postcomment", response_model=ResultObject, summary="Create a comment at Post.")
def add_comment(request:Request, postcomment: PostCommentCreate, db: Session = Depends(get_db)):
    return add_one_comment(request=request, postcomment=postcomment, db=db)

@post_route.post("/postimage", response_model=ResultObject, summary="Add Path of File at Post.")
def add_file(request:Request, postfile: PostFileCreate, db: Session = Depends(get_db)):
    return add_one_file(request=request, postfile=postfile, db=db)

@post_route.delete("/postimage/{id}", response_model=ResultObject, summary="Remove File asociate at Post by its ID.")
def delete_post_image(request:Request, post_id: str, file_id: str, db: Session = Depends(get_db)):
    return remove_one_file(request=request, db=db, post_id=post_id, file_id=str(file_id))
