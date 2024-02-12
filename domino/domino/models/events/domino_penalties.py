import uuid
from datetime import date, datetime
from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean, Text, DateTime, Float
from ...config.db import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())

class PenaltyTypes(Base):
    """Class Penalty Types. Manage all functionalities for Penalty Types."""
 
    __tablename__ = "penalty_types"
    __table_args__ = {'schema' : 'events'}
     
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    description = Column(String(250), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    def dict(self):
        return {
            "id": self.id,
            "card_colour": self.card_colour,
            "description": self.description, 
            "is_active": self.is_active            
        }
        
class DominoBoletusPenalties(Base):
    """DominoBoletusPenalties Class contains standard information for  Domino Penalties at Rounds."""
 
    __tablename__ = "domino_boletus_penalties"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    boletus_id = Column(String, ForeignKey("events.domino_boletus.id"))
    pair_id = Column(String, ForeignKey("events.domino_rounds_pairs.id"))
    player_id = Column(String, ForeignKey("events.players.id"))
    single_profile_id = Column(String)
    penalty_type = Column(String) 
    penalty_amount = Column(Integer)
    penalty_value = Column(Integer)
    apply_points = Column(Boolean)
       
    boletus = relationship("DominoBoletus")
    
    def dict(self):
        return {
            "id": self.id,
            "boletus_id": self.boletus_id,
            "pair_id": self.pair_id,
            "player_id": self.player_id,
            "single_profile_id": self.single_profile_id,
            "penalty_type": self.penalty_type,
            "card_colour": self.card_colour,
            "penalty_value": self.penalty_value
            }