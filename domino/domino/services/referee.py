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
from domino.models.tourney import Referees
from domino.schemas.referee import RefereeBase
from domino.schemas.result_object import ResultObject
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.services.status import get_one_by_name, get_one as get_one_status
from domino.services.users import get_one_by_username
from domino.app import _

def new_referee(tourney_id: str, user_id: str, username:str, db: Session):
    
    one_referee = Referees(tourney_id=tourney_id, user_id=user_id,
                           created_by=username, updated_by=username, is_active=True)
    try:
        db.add(one_referee)
        db.commit()
        return True
    except (Exception, SQLAlchemyError) as e:
        return False
    