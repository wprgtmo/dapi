
"""coding=utf-8."""

from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional
        
        
class DominoScaleCreated(BaseModel):
    player_id: str
    position_number: str
    