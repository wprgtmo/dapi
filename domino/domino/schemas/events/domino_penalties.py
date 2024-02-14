
"""coding=utf-8."""

from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional
        
class DominoPenaltiesCreated(BaseModel):
    player_id: str
    penalty_type: str
    penalty_value: int
    
class DominoAnnulledCreated(BaseModel):
    player_id: str
    annulled_type: str
    was_expelled: bool
    
class DominoAbsencesCreated(BaseModel):
    players: str
