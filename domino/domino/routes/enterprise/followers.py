# Routes status.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict
from domino.app import get_db
from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.enterprise.userprofile import ProfileFollowersBase
from domino.schemas.resources.result_object import ResultObject

from domino.services.enterprise.followers import get_follower_suggestions_at_profile, add_one_followers, \
    remove_one_followers, get_all_followers
  
follower_route = APIRouter(
    tags=["ProfileFollower"],  
    dependencies=[Depends(JWTBearer())]   
)

@follower_route.get("/profile/suggestions/{profile_id}", response_model=Dict, summary="Get list of Profile Suggestions")
def get_follower_suggestions(
    request: Request,
    profile_id: str,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_follower_suggestions_at_profile(request=request, profile_id=profile_id, page=page, 
                                               per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)


@follower_route.get("/profile/followers/", response_model=Dict, summary="Get list of Followers.")
def get_followers(
    request: Request,
    profile_id: str,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all_followers(request=request, profile_id=profile_id, page=page, 
                             per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@follower_route.post("/profile/followers", response_model=ResultObject, summary="Add Followers at Profile")
def add_followers(request:Request, profilefollower: ProfileFollowersBase, db: Session = Depends(get_db)):
    return add_one_followers(request=request, db=db, profilefollower=profilefollower)

@follower_route.delete("/profile/followers/", response_model=ResultObject, summary="Remove Followers at Profile")
def delete_followers(request:Request, profile_id: str, profile_follower_id: str, db: Session = Depends(get_db)):
    return remove_one_followers(request=request, db=db, profile_id=profile_id, profile_follower_id=profile_follower_id)


