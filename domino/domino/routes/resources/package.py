from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict

from starlette import status
from domino.auth_bearer import JWTBearer

from domino.schemas.resources.package import PackagesBase, PackagesSchema
from domino.schemas.resources.result_object import ResultObject, ResultData

from domino.services.resources.package import get_all, new, get_one_by_id, delete, update
  
packages_route = APIRouter(
    tags=["Packages"],
    dependencies=[Depends(JWTBearer())]   
)

@packages_route.get("/packages", response_model=Dict, summary="Obtain a list of Packages to be Commercialized.")
def get_packages(
    request: Request,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, page=page, per_page=per_page, criteria_key=criteria_key, criteria_value=criteria_value, db=db)

@packages_route.get("/packages/{id}", response_model=ResultObject, summary="Get a Package for your ID.")
def get_package_by_id(id: int, db: Session = Depends(get_db)):
    return get_one_by_id(package_id=id, db=db)

@packages_route.post("/packages", response_model=ResultObject, summary="Create a Package.")
def create_package(request:Request, package: PackagesBase, db: Session = Depends(get_db)):
    return new(request=request, package=package, db=db)

@packages_route.delete("/packages/{id}", response_model=ResultObject, summary="Deactivate a Package by its ID.")
def delete_package(request:Request, id: int, db: Session = Depends(get_db)):
    return delete(request=request, package_id=str(id), db=db)
    
@packages_route.put("/packages/{id}", response_model=ResultObject, summary="Update a Package by its ID")
def update_package(request:Request, id: int, package: PackagesBase, db: Session = Depends(get_db)):
    return update(request=request, db=db, package_id=str(id), package=package)
