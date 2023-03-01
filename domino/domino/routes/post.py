from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.post import PostBase, PostLikeCreate, PostCommentCreate, PostShareCreate
from domino.schemas.result_object import ResultObject, ResultData
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from domino.services.post import get_all, new, get_one_by_id, delete, update, add_one_likes, add_one_comment, add_one_share
from starlette import status
from domino.auth_bearer import JWTBearer
  
post_route = APIRouter(
    tags=["Post"],
    dependencies=[Depends(JWTBearer())]   
)

@post_route.get("/post", response_model=Dict, summary="Obtain a list of Post.")
def get_post(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@post_route.get("/post/{id}", response_model=ResultObject, summary="Get a Post for your ID.")
def get_post_by_id(id: int, db: Session = Depends(get_db)):
    return get_one_by_id(post_id=id, db=db)

@post_route.post("/post", response_model=ResultObject, summary="Create a Post.")
def create_post(request:Request, post: PostBase, db: Session = Depends(get_db)):
    return new(request=request, post=post, db=db)

@post_route.delete("/post/{id}", response_model=ResultObject, summary="Deactivate a Post by its ID.")
def delete_post(request:Request, id: int, db: Session = Depends(get_db)):
    return delete(request=request, post_id=str(id), db=db)
    
@post_route.put("/post/{id}", response_model=ResultObject, summary="Update a Post by its ID")
def update_post(request:Request, id: int, post: PostBase, db: Session = Depends(get_db)):
    return update(request=request, db=db, post_id=str(id), post=post)

@post_route.post("/postlike", response_model=ResultObject, summary="Create a like at Post.")
def add_like(request:Request, postlike: PostLikeCreate, db: Session = Depends(get_db)):
    return add_one_likes(request=request, postlike=postlike, db=db)

@post_route.post("/postcomment", response_model=ResultObject, summary="Create a comment at Post.")
def add_comment(request:Request, postcomment: PostCommentCreate, db: Session = Depends(get_db)):
    return add_one_comment(request=request, postcomment=postcomment, db=db)

@post_route.post("/postshare", response_model=ResultObject, summary="Share Post.")
def add_share(request:Request, postshare: PostShareCreate, db: Session = Depends(get_db)):
    return add_one_share(request=request, postshare=postshare, db=db)
