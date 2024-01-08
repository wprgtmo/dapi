
"""coding=utf-8."""

from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional
        
        
class DominoManualScaleCreated(BaseModel):
    id: str
    number: int
    
class DominoAutomaticScaleCreated(BaseModel):
    id: str
    title: str
    min: float
    max: float
    
class DominoRoundsCreated(BaseModel):
    id: Optional[str]
    round_number: Optional[int]
    is_first: Optional[bool]
    is_last: Optional[bool]
    
    can_segment: Optional[bool]
    use_segmentation: Optional[str]
    
    can_bonus: Optional[bool]
    use_bonus: Optional[str]
    amount_bonus_tables: Optional[int]
    amount_bonus_points: Optional[float]
    
    amount_tables: Optional[int]
    amount_tables_playing: Optional[int]
    amount_categories: Optional[int]
    amount_players_playing: Optional[int]
    amount_players_waiting: Optional[int]
    amount_players_pause: Optional[int]
    amount_players_expelled: Optional[int]
    
    status_id: Optional[int]
    status_name: Optional[str]
    status_description: Optional[str]
    
    modality: Optional[str]
    
class DominoRoundsAperture(BaseModel):
    id: Optional[str]
    round_number: Optional[int]
    
    use_segmentation: Optional[str]
    use_bonus: Optional[str]
    amount_bonus_tables: Optional[int]
    amount_bonus_points: Optional[float]
    