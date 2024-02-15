"""coding=utf-8."""

from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional
 
class TourneyBase(BaseModel):
    name: str
    event_id: str
    modality: Optional[str]
    summary: Optional[str]
    
    start_date: Optional[date] = date.today()
    
    @validator('name')
    def name_not_empty(cls, name):
        if not name:
            raise ValueError('Nombre de Torneo es Requerido')
        return name
    
    @validator('event_id')
    def event_id_not_empty(cls, event_id):
        if not event_id:
            raise ValueError('Id del Evento es Requerida')
        return event_id
    
    @validator('modality')
    def modality_not_empty(cls, modality):
        if not modality:
            raise ValueError('Modalidad del torneo es Requerida')
        return modality
    
class TourneySchema(TourneyBase):
    id: Optional[int]
    
    status_id: int
    created_by: str
    created_date: datetime = datetime.today()
    updated_by: str
    updated_date: datetime = datetime.today()
    
    class Config:
        orm_mode = True
        
class TourneyCreated(BaseModel):
    name: Optional[str]
    modality: Optional[str]
    summary: Optional[str]
    startDate: Optional[date]
    number_rounds: Optional[int]
    
class SettingTourneyCreated(BaseModel):
    
    name: Optional[str]
    modality: Optional[str]
    summary: Optional[str]
    start_date: Optional[date]
    number_rounds: Optional[int]
    
    amount_tables: Optional[int] 
    amount_smart_tables: Optional[int] 
    number_points_to_win: Optional[int] 
    time_to_win: Optional[int] 
    lottery: Optional[str] 
    constant_increase_ELO: Optional[float]
    
    # use_penalty: Optional[bool]
    # limitPenaltyPoints: Optional[int]
    # points_penalty_yellow: Optional[int]
    # points_penalty_red: Optional[int]
    
    points_for_absences: Optional[int]
    
    use_segmentation: Optional[bool]
    
    amount_segmentation_round: Optional[int] 
    
    # use_bonus: Optional[bool]
    # amount_bonus_tables: Optional[int]
    # amount_bonus_points: Optional[int]
    # amount_bonus_points_rounds: Optional[int]
     
    round_ordering_one: Optional[str] 
    round_ordering_dir_one: Optional[str] 
    round_ordering_two: Optional[str]
    round_ordering_dir_two: Optional[str] 
    round_ordering_three: Optional[str]
    round_ordering_dir_three: Optional[str] 
    
    event_ordering_one: Optional[str]
    event_ordering_dir_one: Optional[str] 
    event_ordering_two: Optional[str]
    event_ordering_dir_two: Optional[str] 
    event_ordering_three: Optional[str]
    event_ordering_dir_three: Optional[str] 
    
    scope_tourney: Optional[str]
    level_tourney: Optional[str]
    
class DominoCategoryCreated(BaseModel):
    category_number: str
    elo_min: float
    elo_max: float
    amount_players: int = 0
    