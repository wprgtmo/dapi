
"""coding=utf-8."""

from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional
        
        
class DominoDataCreated(BaseModel):
    pair: str
    point: int
    close_for_time: bool
