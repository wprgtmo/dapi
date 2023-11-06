"""coding=utf-8."""

import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, Text, Float, DateTime
from ...config.db import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())

class Notifications(Base):
    """Notifications Class contains standard information for a Notifications."""
 
    __tablename__ = "notifications"
    __table_args__ = {'schema' : 'notifications'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)
    subject = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    read_date = Column(DateTime, nullable=False, default=datetime.now())
    remove_date = Column(DateTime, nullable=False, default=datetime.now())
    is_active = Column(Boolean, nullable=False, default=True)
    
    def dict(self):
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "subject": self.subject,
            "summary": self.summary,
            "is_read": self.is_read,
            'created_by': self.created_by,
            "is_active": self.is_active,
            "created_date": self.created_date,
            "read_date": self.read_date,
            "remove_date": self.remove_date
            }
