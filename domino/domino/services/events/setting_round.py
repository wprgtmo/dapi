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
from domino.auth_bearer import decodeJWT
from domino.functions_jwt import get_current_user
from domino.config.config import settings
from domino.app import _
from fastapi.responses import FileResponse
from os import getcwd

from domino.models.events.domino_round import DominoRounds, DominoRoundsPairs
from domino.models.events.tourney import SettingTourney

from domino.schemas.events.events import EventBase, EventSchema
from domino.schemas.resources.result_object import ResultObject

from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
from domino.services.enterprise.users import get_one_by_username
from domino.services.enterprise.userprofile import get_one as get_one_profile
from domino.services.events.domino_boletus import created_boletus_for_round

from domino.services.events.domino_round import configure_rounds
from domino.services.events.domino_scale import new_initial_automatic_round, new_initial_manual_round

def configure_round_for_tourney(tourney_id: str, round_id: str, modality:str, db: Session):

    # si la modalidad es pareja, es vaciar la tabla del escalafón.
    # si es individual, aplico el algoritmo de distribuir por mesas...
    
    if modality == 'Parejas':
        create_pair_for_profile_pair(tourney_id, round_id, db=db, created_by='miry')
    else:
        create_pair_for_profile_single(tourney_id, round_id, db=db, created_by='miry')
        
    db.commit()    
    
    return True  