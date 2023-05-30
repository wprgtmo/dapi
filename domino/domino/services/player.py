import math
import uuid

from datetime import datetime
from fastapi import HTTPException, Request, UploadFile, File
from unicodedata import name
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
import json

from domino.config.config import settings
from domino.models.tourney import Players
from domino.schemas.player import PlayerBase
from domino.schemas.result_object import ResultObject
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.services.status import get_one_by_name, get_one as get_one_status
from domino.services.users import get_one_by_username
from domino.app import _

def new_player(tourney_id: str, user_id: str, username:str, db: Session):
    
    one_player = Players(tourney_id=tourney_id, user_id=user_id, nivel='NORMAL',
                         created_by=username, updated_by=username, is_active=True)
    try:
        db.add(one_player)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        return False
    
def remove_player(tourney_id: str, user_id: str, db: Session):
    
    try:
        db_player = db.query(Players).filter(Players.tourney_id == tourney_id, Players.user_id == user_id,).first()
        db.delete(db_player)
        db.commit()
    except (Exception, SQLAlchemyError) as e:
        print(e)
        raise HTTPException(status_code=404, detail="No es posible eliminar")
    return True
    
