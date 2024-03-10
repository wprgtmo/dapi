from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer

# from domino.schemas.enterprise.userprofile import FederatedProfile
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.enterprise.userprofile import get_all_federated_profile
 
federative_route = APIRouter(
    tags=["Profile"],
    dependencies=[Depends(JWTBearer())]   
)

@federative_route.get("/federative", response_model=ResultData, summary="Obtain a list of Federated profile")
def get_profile(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    search: str = "",
    db: Session = Depends(get_db)
):
    return get_all_federated_profile(request=request, page=page, per_page=per_page, criteria_value=search, db=db)