# Routes user.py
"""coding=utf-8."""

import uuid
from datetime import date
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, Text, Float
from ...config.db import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())

class Tourney(Base):
    """Tourney Class contains standard information for a Tourney."""
 
    __tablename__ = "tourney"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, ForeignKey("events.events.id"), nullable=False)
    modality = Column(String(30), nullable=False)
    name = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    close_date = Column(Date, nullable=True)
    
    amount_tables = Column(Integer, nullable=False, default=1)
    amount_smart_tables = Column(Integer, nullable=False, default=0)
    amount_rounds = Column(Integer, nullable=False, default=1)
    
    number_points_to_win = Column(Integer, nullable=False, default=0)
    time_to_win = Column(Integer, nullable=False, default=0)
    game_system = Column(String(120), nullable=True)
    lottery_type = Column(String(120), nullable=True)
    penalties_limit = Column(Integer, nullable=True, default=0)
    
    image = Column(Text, nullable=True)
    
    use_bonus = Column(Boolean, nullable=True, default=False)
    use_segmentation = Column(Boolean, nullable=True, default=False)
    amount_bonus_tables = Column(Integer, nullable=True, default=0)
    amount_bonus_points = Column(Integer, nullable=True, default=0)
    number_rounds = Column(Integer, nullable=True, default=0)
    number_bonus_round = Column(Integer, nullable=True, default=0)
    elo_min = Column(Float, nullable=True)
    elo_max = Column(Float, nullable=True)
    constant_increase_elo = Column(Float, nullable=True)
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)  # perfil que lo creo
    
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    
    round_ordering_one = Column(String(120), nullable=True)
    round_ordering_two = Column(String(120), nullable=True)
    round_ordering_three = Column(String(120), nullable=True)
    round_ordering_four = Column(String(120), nullable=True)
    round_ordering_five = Column(String(120), nullable=True)
    
    event_ordering_one = Column(String(120), nullable=True)
    event_ordering_two = Column(String(120), nullable=True)
    event_ordering_three = Column(String(120), nullable=True)
    event_ordering_four = Column(String(120), nullable=True)
    event_ordering_five = Column(String(120), nullable=True)
    
    points_penalty_yellow = Column(Integer, nullable=True, default=0)
    points_penalty_red = Column(Integer, nullable=True, default=0)
    
    event = relationship("Event", back_populates="tourneys")
    
    status = relationship("StatusElement")
    
    def dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "modality": self.modality,
            "name": self.name,
            "summary": self.summary,
            "start_date": self.start_date,
            "status_id": self.status_id,
            "profile_id": self.profile_id,
            "amount_tables": self.amount_tables,
            "amount_smart_tables": self.amount_smart_tables,
            "amount_rounds": self.amount_rounds,
            "use_bonus": 'YES' if self.use_bonus else 'NO',
            "amount_bonus_tables": self.amount_bonus_tables,
            "amount_bonus_points": self.amount_bonus_points,
            "number_bonus_round": self.number_bonus_round,
            "number_points_to_win": self.number_points_to_win,
            "time_to_win": self.time_to_win,
            "game_system": self.game_system,
            'lottery_type': self.lottery_type,
            'penalties_limit': self.penalties_limit,
            'image': self.image,
        }
    
        
class GameRules(Base):
    """Game rules Class contains standard information for game rules of Tourney.""" 

    __tablename__ = "gamerules"
    __table_args__ = {'schema' : 'events'}
    
    tourney_id = Column(String, ForeignKey("events.tourney.id"), primary_key=True)
    amount_points = Column(Integer, nullable=True, default=100)
    amount_time = Column(Integer, nullable=True, default=60)
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "amount_points": self.amount_points,
            "amount_time": self.amount_time
        }
class TraceLotteryManual(Base):
    """TraceLotteryManual contains standard information for setting of manual lottery.""" 

    __tablename__ = "trace_lottery_manual"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"))
    modality = Column(String(30), nullable=False)
    position_number = Column(Integer, nullable=False)
    player_id = Column(String, ForeignKey("events.players.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "modality": self.modality,
            "position_number": self.position_number,
            "player_id": self.player_id,
            "is_active": self.is_active
            }
        

class DominoCategory(Base):
    """DominoCategory Class contains standard information for  Domino categories at Torney."""
 
    __tablename__ = "domino_categories"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False)
    category_number = Column(String(100), nullable=False)
    position_number = Column(Integer, nullable=False)
    elo_min = Column(Float, nullable=False)
    elo_max = Column(Float, nullable=False)
    amount_players = Column(Integer, nullable=False)
    
    tourney = relationship('Tourney')
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "category_number": self.category_number,
            "position_number": self.position_number,
            "elo_min": self.elo_min,
            "elo_max": self.elo_max,
            'amount_players': self.amount_players
            }