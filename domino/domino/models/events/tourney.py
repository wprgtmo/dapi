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
    # close_date = Column(Date, nullable=False)
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    # manage_id = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)  # perfil que lo creo
    
    # settingtourney = relationship("SettingTourney")
    
    def dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "modality": self.modality,
            "name": self.name,
            "summary": self.summary,
            "start_date": self.start_date,
            "status_id": self.status_id,
            "profile_id": self.profile_id
        }
    
class Players(Base):
    """Players Class contains standard information for a Players of Tourney."""

    __tablename__ = "players"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False)
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)
    nivel = Column(String(50), nullable=True)  # nivel del jugador en ese torneo
    invitation_id = Column(String, ForeignKey("events.invitations.id"), nullable=False)
    
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    is_active = Column(Boolean, nullable=False, default=True)
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "profile_id": self.profile_id,
            "nivel": self.nivel,
            "invitation_id": self.invitation_id
        }
        
class Referees(Base):
    """Referees Class contains standard information for a Referees of Tourney."""

    __tablename__ = "referees"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False, primary_key=True)
    profile_id = Column(String, ForeignKey("enterprise.profile_member.id"), nullable=False)
    invitation_id = Column(String, ForeignKey("events.invitations.id"), nullable=False)
    
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    is_active = Column(Boolean, nullable=False, default=True)
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "user_id": self.user_id
        }
    
# Los patrocinadores son de eventos    
# class Sponsors(Base):
#     """Sponsors Class contains standard information for a Sponsors of Tourney.""" # patrocinadores

#     __tablename__ = "sponsors"
#     __table_args__ = {'schema' : 'events'}
    
#     id = Column(Integer, primary_key=True)
#     tourney_id = Column(String, ForeignKey("events.tourney.id"))
#     name = Column(Text, nullable=False)
    
#     created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
#     created_date = Column(Date, nullable=False, default=date.today())
#     updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
#     updated_date = Column(Date, nullable=False, default=date.today())
    
#     is_active = Column(Boolean, nullable=False, default=True)
    
#     def dict(self):
#         return {
#             "id": self.id,
#             "tourney_id": self.tourney_id,
#             "name": self.name
#         }
        
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

class SettingTourney(Base):
    """Setting Tourney Class contains standard information for setting of Tourney.""" 

    __tablename__ = "setting_tourney"
    __table_args__ = {'schema' : 'events'}
    
    tourney_id = Column(String, ForeignKey("events.tourney.id"), primary_key=True)
    amount_tables = Column(Integer, nullable=False, default=1)
    amount_smart_tables = Column(Integer, nullable=False, default=0)
    amount_rounds = Column(Integer, nullable=False, default=1)
    
    use_bonus = Column(Boolean, nullable=False, default=False)
    amount_bonus_tables = Column(Integer, nullable=False, default=0)
    amount_bonus_points = Column(Integer, nullable=False, default=0)
    number_bonus_round = Column(Integer, nullable=False, default=0)
    image = Column(Text, nullable=True)
    
    number_points_to_win = Column(Integer, nullable=False, default=0)
    time_to_win = Column(Integer, nullable=False, default=0)
    game_system = Column(String(120), nullable=False)
    lottery_type = Column(String(120), nullable=False)
    
    penalties_limit = Column(Integer, nullable=False, default=0)
    
    def dict(self):
        return {
            "tourney_id": self.tourney_id,
            "amount_tables": self.amount_tables,
            "amount_smart_tables": self.amount_smart_tables,
            "amount_bonus_tables": self.amount_bonus_tables,
            "amount_bonus_points": self.amount_bonus_points,
            "number_bonus_round": self.number_bonus_round,
            "amount_rounds": self.amount_rounds,
            "number_points_to_win": self.number_points_to_win,
            "time_to_win": self.time_to_win,
            "game_system": self.game_system,
            'lottery_type': self.lottery_type,
            'penalties_limit': self.penalties_limit
        }
            
# class Pairs(Base):
#     """Pairs Class contains standard information for Pairs of domino of Tourney.""" 

#     __tablename__ = "pairs"
#     __table_args__ = {'schema' : 'events'}
    
#     id = Column(String, primary_key=True, default=generate_uuid)
#     tourney_id = Column(String, ForeignKey("events.tourney.id"))
#     one_player = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
#     two_player = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
#     name = Column(String(100), nullable=True)
    
#     amount_points = Column(Integer, nullable=True, default=100)
#     amount_time = Column(Integer, nullable=True, default=60)
    
#     created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
#     created_date = Column(Date, nullable=False, default=date.today())
#     updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
#     updated_date = Column(Date, nullable=False, default=date.today())
    
#     is_active = Column(Boolean, nullable=False, default=True)
    
#     def dict(self):
#         return {
#             "tourney_id": self.tourney_id,
#             "amount_points": self.amount_points,
#             "amount_time": self.amount_time
#         }