"""coding=utf-8."""
 
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List

class NotificationsBase(BaseModel):
    profile_id: str
    subject: str
    summary: str
       
    @validator('subject')
    def subject_not_empty(cls, subject):
        if not subject:
            raise ValueError('Asunto de la Notificación es Requerido')
        return subject
    
    @validator('summary')
    def summary_not_empty(cls, summary):
        if not summary:
            raise ValueError('Comentario de Post Requerido')
        return summary
    
class NotificationsSchema(NotificationsBase):
    id: Optional[int]
    
    created_by: str
    created_date: datetime = datetime.now()
    read_date: datetime = datetime.today()
    remove_date: datetime = datetime.today()
    is_active: bool = True
    is_read: bool = False
    
    class Config:
        orm_mode = True