
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
    