"""coding=utf-8."""

from email.policy import default
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import String, DateTime, Integer
from ...config.db import Base

class ExtTypes(Base):
    """ExtTypes Class contains standard information for a ExtTypes."""
 
    __tablename__ = "ext_types"
    __table_args__ = {'schema' : 'resources'}
    
    id = Column(Integer, primary_key=True)
    ext_code = Column(String(10), nullable=False, unique=True)
    type_file = Column(String(10), nullable=False)
    created_by = Column(String(50), nullable=False, default='foo')
    created_date = Column(DateTime, nullable=False, default=datetime.now())
    
    def dict(self):
        return {
            "id": self.id,
            "ext_code": self.ext_code,
            "type_file": self.type_file,
            "created_by": self.created_by,
            "created_date": self.created_date
        }
