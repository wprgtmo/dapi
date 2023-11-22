from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import List, Dict
from starlette import status
from domino.auth_bearer import JWTBearer
from fastapi.responses import FileResponse, JSONResponse
from os import getcwd, remove
from typing import Optional

from domino.schemas.events.tourney import SettingTourneyCreated, DominoCategoryCreated
from domino.schemas.resources.result_object import ResultObject

from domino.services.events.domino_table import get_all, delete, update
from domino.services.events.setting_tourney import get_one_configure_tourney
from domino.services.events.tourney import configure_one_tourney, save_image_tourney, configure_categories_tourney
  
settingtourney_route = APIRouter(
    tags=["SettingTourney"],
    dependencies=[Depends(JWTBearer())]   
)

@settingtourney_route.get("/tourney/setting/configure_tables", response_model=Dict, summary="Obtain a list of Domino Tables of Tourney.")
def get_dominotables(
    request: Request,
    profile_id: str,
    tourney_id: str,
    page: int = 1, 
    per_page: int = 6, 
    criteria_key: str = "",
    criteria_value: str = "",
    db: Session = Depends(get_db)
):
    return get_all(request=request, profile_id=profile_id, tourney_id=tourney_id, page=page, per_page=per_page, 
                   criteria_key=criteria_key, criteria_value=criteria_value, db=db)
    
@settingtourney_route.put("/tourney/setting/configure_tables/{id}", response_model=ResultObject, summary="Update of Domino Tables by id")
def update_dominotables(request:Request, id: str, image: UploadFile = None, db: Session = Depends(get_db)):
    return update(request=request, db=db, id=str(id), file=image)

@settingtourney_route.delete("/tourney/setting/configure_tables/{id}", response_model=ResultObject, summary="Deactivate a Domino Table by its ID.")
def delete_dominotable(request:Request, id: str, db: Session = Depends(get_db)):
    return delete(request=request, table_id=str(id), db=db)

@settingtourney_route.get("/tourney/setting/{tourney_id}", response_model=Dict, summary="Get Configure Tourney..")
def get_configure_tourney(request:Request, tourney_id: str, db: Session = Depends(get_db)):
    return get_one_configure_tourney(request=request, tourney_id=tourney_id, db=db)

@settingtourney_route.post("/tourney/setting/{id}", response_model=ResultObject, summary="Configure Tourney..")
def configure_tourney(request:Request, id: str, settingtourney: SettingTourneyCreated = Depends(), 
                      db: Session = Depends(get_db)):
    return configure_one_tourney(request=request, tourney_id=id, settingtourney=settingtourney.dict(), db=db)  

@settingtourney_route.post("/tourney/setting/images/{id}", response_model=ResultObject, summary="Configure Image of Tourney..")
def configure_setting_image(request:Request, id: str, image: UploadFile = None, db: Session = Depends(get_db)):
    return save_image_tourney(request=request, tourney_id=id, file=image, db=db)

@settingtourney_route.post("/tourney/setting/categories/{id}", response_model=ResultObject, summary="Configure categories of Tourney..")
def configure_setting_categories(request:Request, id: str, lst_categories: List[DominoCategoryCreated], db: Session = Depends(get_db)):
    return configure_categories_tourney(request=request, tourney_id=id, lst_categories=lst_categories, db=db)
    
  