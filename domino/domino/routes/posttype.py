from fastapi import APIRouter, Depends, HTTPException, Request
from domino.schemas.post import PostTypeBase
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from domino.services.posttype import get_all, new
from starlette import status
from domino.auth_bearer import JWTBearer
  
posttype_route = APIRouter(
    tags=["Post Type"],
    dependencies=[Depends(JWTBearer())]   
)

@posttype_route.get("/posttype", response_model=Dict, summary="Get list of Types of Post")
def get_status(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@posttype_route.post("/posttype", response_model=ResultObject, summary="Create a new type of post.")
def create_posttype(request:Request, posttype: PostTypeBase, db: Session = Depends(get_db)):
    return new(request=request, posttype=posttype, db=db)
