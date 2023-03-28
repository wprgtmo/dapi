from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.post import PostBase, PostUpdated
from domino.schemas.postelement import PostLikeCreate, PostCommentCreate, PostFileCreate, CommentCommentCreate, CommentLikeCreate, PostPathsCreate
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.post import get_all, new, get_one_by_id, delete, update, add_one_likes, add_one_comment, \
    add_paths_at_post, remove_one_file, add_one_likes_at_comment, add_one_comment_at_comment, get_list_post
from starlette import status
from domino.auth_bearer import JWTBearer
  
post_route = APIRouter(
    tags=["Post"],
    dependencies=[Depends(JWTBearer())]   
)

@post_route.get("/post/all", response_model=Dict, summary="Obtain a list of Post.")
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

@post_route.get("/post/{id}", response_model=ResultObject, summary="Get a Post for your ID.")
def get_post_by_id(id: str, db: Session = Depends(get_db)):
    return get_one_by_id(post_id=id, db=db)

@post_route.post("/post", response_model=ResultObject, summary="Create a Post.")
def create_post(request:Request, post: PostBase, db: Session = Depends(get_db)):
    return new(request=request, post=post, db=db)

@post_route.delete("/post/{id}", response_model=ResultObject, summary="Deactivate a Post by its ID.")
def delete_post(request:Request, id: str, db: Session = Depends(get_db)):
    return delete(request=request, post_id=str(id), db=db)
    
@post_route.put("/post/{id}", response_model=ResultObject, summary="Update a Post by its ID")
def update_post(request:Request, id: str, post: PostUpdated, db: Session = Depends(get_db)):
    return update(request=request, db=db, post_id=str(id), post=post)

@post_route.post("/postlike", response_model=ResultObject, summary="Create a like at Post.")
def add_like(request:Request, postlike: PostLikeCreate, db: Session = Depends(get_db)):
    return add_one_likes(request=request, postlike=postlike, db=db)

@post_route.post("/postcomment", response_model=ResultObject, summary="Create a comment at Post.")
def add_comment(request:Request, postcomment: PostCommentCreate, db: Session = Depends(get_db)):
    return add_one_comment(request=request, postcomment=postcomment, db=db)

@post_route.post("/postimage", response_model=ResultObject, summary="Add Path of File at Post.")
def add_file(request:Request, postpath: PostPathsCreate, db: Session = Depends(get_db)):
    return add_paths_at_post(request=request, postpaths=postpath, db=db)

@post_route.delete("/postimage/{id}", response_model=ResultObject, summary="Remove File asociate at Post by its ID.")
def delete_post_image(request:Request, id: str, db: Session = Depends(get_db)):
    return remove_one_file(request=request, db=db, postimage_id=str(id))

@post_route.post("/commentlike", response_model=ResultObject, summary="Create a like at Comment.")
def add_like_at_comment(request:Request, commentlike: CommentLikeCreate, db: Session = Depends(get_db)):
    return add_one_likes_at_comment(request=request, commentlike=commentlike, db=db)

@post_route.post("/commentcomment", response_model=ResultObject, summary="Create a comment at Comment")
def add_comment_at_comment(request:Request, commentcomment: CommentCommentCreate, db: Session = Depends(get_db)):
    return add_one_comment_at_comment(request=request, commentcomment=commentcomment, db=db)