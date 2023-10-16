
import uuid
from datetime import date
from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean, Text, DateTime
from ...config.db import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())

class DominoBoletus(Base):
    """DominoPositions Class contains standard information for  Domino Positions at Rounds."""
 
    __tablename__ = "domino_boletus"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False)
    round_id = Column(String, ForeignKey("events.domino_rounds.id"), nullable=False)
    table_id = Column(String, ForeignKey("events.domino_tables.id"), nullable=False)
    player_id = Column(String, ForeignKey("events.players.id"), nullable=False)
    is_valid = Column(Boolean, nullable=False, default=True)
    is_winner = Column(Boolean, nullable=False, default=False)
    
    boletus_position = relationship("DominoBoletusPosition")
    
    tourney = ("Tourney")
    
    def dict(self):
        return {
            "id": self.id,
            "tourney_id": self.tourney_id,
            "round_id": self.round_id,
            "table_id": self.table_id,
            "player_id": self.player_id,
            "is_valid": self.is_valid,
            "is_winner": self.is_winner
            }
        
class DominoBoletusPosition(Base):
    """DominoBoletusPosition Class contains standard information for  Domino Positions at Rounds."""
 
    __tablename__ = "domino_boletus_position"
    __table_args__ = {'schema' : 'events'}
    
    boletus_id = Column(String, ForeignKey("events.domino_boletus.id"), primary_key=True, )
    position_id = Column(Integer, primary_key=True)
    single_profile_id = Column(String) 
    
    def dict(self):
        return {
            "boletus_id": self.boletus_id,
            "position_id": self.position_id,
            "single_profile_id": self.single_profile_id
            }