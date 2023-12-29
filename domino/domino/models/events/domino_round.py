"""coding=utf-8."""

import uuid
from datetime import date
from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean, Text, DateTime, Float
from ...config.db import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())

class DominoRounds(Base):
    """DominoRounds Class contains standard information for  Domino rounds at Torney."""
 
    __tablename__ = "domino_rounds"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    summary = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    close_date = Column(DateTime, nullable=False)
    
    is_first = Column(Boolean, nullable=False, default=False)
    is_last = Column(Boolean, nullable=False, default=False)
    
    use_segmentation = Column(Boolean, nullable=False, default=False)
    use_bonus = Column(Boolean, nullable=False, default=False)
    amount_bonus_tables = Column(Integer, nullable=False, default=0)
    amount_bonus_points = Column(Integer, nullable=False, default=0)
    
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=True)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    
    tourney = relationship('Tourney')
    
    idx_number_table = UniqueConstraint('tourney_id', 'round_number')
    
    def dict(self):
        return {
            "id": self.id,
            "tourney_id": self.tourney_id,
            "round_number": self.round_number,
            "summary": self.summary,
            "start_date": self.start_date,
            "close_date": self.close_date,
            'status_id': self.status_id
            }

class DominoRoundsScale(Base):
    """DominoRoundsScale Class contains standard information for  Domino Scale at Rounds."""
 
    __tablename__ = "domino_rounds_scale"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False)
    round_id = Column(String, ForeignKey("events.domino_rounds.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    position_number = Column(Integer, nullable=False)
    player_id = Column(String, ForeignKey("events.players.id"))
    elo = Column(Float)
    elo_variable = Column(Float)
    games_played = Column(Integer)
    games_won = Column(Integer)
    games_lost = Column(Integer)
    points_positive = Column(Integer)
    points_negative = Column(Integer)
    points_difference = Column(Integer)
    is_active = Column(Boolean, nullable=False, default=True)
    category_id = Column(String)
    
    def dict(self):
        return {
            "id": self.id,
            "tourney_id": self.tourney_id,
            "round_id": self.round_id,
            "round_number": self.round_number,
            "position_number": self.position_number,
            "player_id": self.pairs_id,
            "is_active": self.is_active,
            'category_id': self.category_id
            }
class DominoRoundsPairs(Base):
    """DominoRoundsPairs Class contains standard information for Pairs of domino of Tourney.""" 

    __tablename__ = "domino_rounds_pairs"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"))
    round_id = Column(String, ForeignKey("events.domino_rounds.id"), nullable=False)
    position_number = Column(Integer, nullable=False)
    one_player_id = Column(String, ForeignKey("enterprise.profile_member.id"))
    two_player_id = Column(String, ForeignKey("enterprise.profile_member.id"))
    name = Column(String(100), nullable=True)
    profile_type = Column(String, nullable=False) # Individual 0 Parejas
    player_id = Column(String, ForeignKey("events.players.id"))
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
    is_active = Column(Boolean, nullable=False, default=True)
    scale_number_one_player = Column(Integer) 
    scale_number_two_player = Column(Integer) 
    scale_id_one_player = Column(String) 
    scale_id_two_player = Column(String) 
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "round_id": self.round_id,
            "position_number": self.position_number,
            "one_player_id": self.one_player_id,
            "two_player_id": self.two_player_id,
            "name": self.name,
            "scale_number_one_player": self.scale_number_one_player,
            "scale_number_two_player": self.scale_number_two_player,
            'scale_id_one_player': self.scale_id_one_player,
            'scale_id_two_player': self.scale_id_two_player
        }