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

# from domino.models.events.domino_round import DominoRounds, DominoRoundsPairs
# from domino.models.events.tourney import SettingTourney

# from domino.schemas.events.events import EventBase, EventSchema
from domino.schemas.resources.result_object import ResultObject

# from domino.services.resources.status import get_one_by_name as get_one_status_by_name, get_one as get_one_status
# from domino.services.resources.utils import get_result_count, upfile, create_dir, del_image, get_ext_at_file, remove_dir
# from domino.services.enterprise.users import get_one_by_username
# from domino.services.enterprise.userprofile import get_one as get_one_profile
# from domino.services.events.domino_boletus import created_boletus_for_round

# from domino.services.events.domino_round import configure_rounds
# from domino.services.events.domino_scale import new_initial_automatic_round, new_initial_manual_round

def get_all_data_by_boletus(request:Request, page: int, per_page: int, round_id: str, db: Session):  
    
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    lst_data = [{'number': '1', 'pair_one': 10, 'pair_two': 0}, {'number': '2', 'pair_one': 0, 'pair_two': 20},
                {'number': '3', 'pair_one': 50, 'pair_two': 0}, {'number': '4', 'pair_one': 0, 'pair_two': 182}]
    
    dict_result = {'round_number': '1', 'table_number': '1', 'pair_one': 'Juan - Pepe', 'pair_two': 'Jorge - Joaquin',
                   'data': lst_data}
    
    result.data = dict_result
    
    return result
