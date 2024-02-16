
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
    lottery_type: Optional[str]
    
    use_segmentation: Optional[bool]
    use_bonus: Optional[bool]
    use_penalty: Optional[bool]
    
class DominoRoundsAperture(BaseModel):
    
    use_segmentation: Optional[bool]
    use_bonus: Optional[bool]
    amount_bonus_tables: Optional[int]
    amount_bonus_points: Optional[float]
    
    lottery: Optional[list]
    

class BoletusPrinting(BaseModel):
    
    interval: Optional[str]
    interval_value: Optional[str]
    