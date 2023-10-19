

import uuid
from datetime import date, datetime
from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean, Text, DateTime, Float
from ...config.db import Base

def generate_uuid():
    return str(uuid.uuid4())
class DominoData(Base):
    """DominoData Class contains standard information for  Domino Data at Rounds."""
 
    __tablename__ = "domino_data"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    boletus_id = Column(String, ForeignKey("events.domino_boletus.id"))
    data_number = Column(Integer, nullable=False)
    win_pair_id = Column(String, ForeignKey("events.tourney_pairs.id"))
    win_by_points = Column(Boolean, nullable=False, default=False)
    win_by_time = Column(Boolean, nullable=False, default=False)
    number_points = Column(Integer)
    start_date =  Column(DateTime, nullable=False, default=datetime.now())
    end_date =  Column(DateTime, nullable=False, default=datetime.now())
    duration = Column(Float)  # tiempo en minutos,, despues tengo que ver el tipo  de datos
    
    def dict(self):
        return {
            "id": self.id,
            "boletus_id": self.boletus_id,
            "data_number": self.data_number,
            "win_pair_id": self.win_pair_id,
            "win_by_points": self.win_by_points,
            "number_points": self.number_points,
            "duration": self.duration
            }