import math
import uuid

from datetime import datetime
from fastapi import HTTPException, Request
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

from domino.models.events.domino_penalties import DominoBoletusPenalties

from domino.schemas.resources.result_object import ResultObject
from domino.schemas.events.domino_penalties import DominoPenaltiesCreated

from domino.services.resources.status import get_one_by_name, get_one as get_one_status
from domino.services.events.invitations import get_one_by_id as get_invitation_by_id
from domino.services.events.tourney import get_one as get_torneuy_by_eid, get_info_categories_tourney
from domino.services.events.domino_round import get_last_by_tourney, remove_configurate_round

from domino.services.enterprise.userprofile import get_one as get_one_profile

from domino.services.resources.utils import get_result_count, create_dir, del_image, get_ext_at_file, upfile
from domino.services.enterprise.auth import get_url_avatar

def new(request: Request, player_id: str, domino_penalty: DominoPenaltiesCreated, db: Session):
    locale = request.headers["accept-language"].split(",")[0].split("-")[0];
    
    result = ResultObject() 
    
    one_player = get_one_profile(player_id, db=db)
    if not one_player:
        raise HTTPException(status_code=404, detail=_(locale, "player.profile_not_found"))
    
    # verificar si ya tiene penalidades de ese tipo pasadas, error
    str_query = " SELECT count(id) FROM events.domino_boletus_penalties "+\
        "Where boletus_id='" + domino_penalty.boletus_id + "' and single_profile_id='" + player_id +\
        "' and penalty_type='" + domino_penalty.penalty_type + "'"
    amount_pen = db.execute(str_query).fetchone()[0]
    if amount_pen > 0:
        raise HTTPException(status_code=404, detail=_(locale, "penalty.already_exist"))
    
    one_penalty = DominoBoletusPenalties(id=str(uuid.uuid4()), boletus_id=domino_penalty.boletus_id, pair_id=None,
                                         player_id=None, single_profile_id=one_player.id, penalty_type=domino_penalty.penalty_type,
                                         penalty_amount=1, penalty_value=domino_penalty.penalty_value,
                                         apply_points=True) 
    
    try:
        db.add(one_penalty)
        db.commit()
        return result
    except (Exception, SQLAlchemyError) as e:
        return False