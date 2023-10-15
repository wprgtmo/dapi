

import uuid
from datetime import date
from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean, Text, DateTime
from ...config.db import Base

class DominoData(Base):
    """DominoData Class contains standard information for  Domino Data at Rounds."""
 
    __tablename__ = "domino_data"
    __table_args__ = {'schema' : 'events'}
    
    boletus_id = Column(String, ForeignKey("events.domino_boletus.id"), primary_key=True, )
    data_number = Column(Integer, nullable=False)
    single_profile_id = Column(String) 
    
    def dict(self):
        return {
            "boletus_id": self.boletus_id,
            "data_number": self.data_number,
            "single_profile_id": self.single_profile_id
            }