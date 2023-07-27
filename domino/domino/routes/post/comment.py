from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.post.post import PostBase, PostUpdated
from domino.schemas.post.postelement import PostLikeCreate, PostCommentCreate, PostFileCreate, CommentCommentCreate, CommentLikeCreate
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.post.post import add_one_likes_at_comment, add_one_comment_at_comment
  
comment_route = APIRouter(
    tags=["Comment"],
    dependencies=[Depends(JWTBearer())]   
)

@comment_route.post("/commentlike", response_model=ResultObject, summary="Create a like at Comment.")
def add_like_at_comment(request:Request, profile_id: str, commentlike: CommentLikeCreate, db: Session = Depends(get_db)):
    return add_one_likes_at_comment(request=request, profile_id=profile_id, commentlike=commentlike, db=db)

@comment_route.post("/commentcomment", response_model=ResultObject, summary="Create a comment at Comment")
def add_comment_at_comment(request:Request, profile_id: str, commentcomment: CommentCommentCreate, db: Session = Depends(get_db)):
    return add_one_comment_at_comment(request=request, profile_id=profile_id, commentcomment=commentcomment, db=db)