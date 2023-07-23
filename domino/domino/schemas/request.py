"""coding=utf-8."""
 
from datetime import datetime, date
from pydantic import BaseModel, validator
from typing import Optional, List


class RequestAccepted(BaseModel):
    # profile_id: str  
    single_profile_id: str
    accept: bool = True