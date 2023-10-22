"""coding=utf-8."""

import uuid
from datetime import date
from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql.sqltypes import String, Integer, Date, Boolean, Text
from ...config.db import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())

class DominoTables(Base):
    """DominoTables Class contains standard information for  Domino tables at Torney."""
 
    __tablename__ = "domino_tables"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tourney_id = Column(String, ForeignKey("events.tourney.id"), nullable=False)
    table_number = Column(Integer, nullable=False)
    is_smart = Column(Boolean, nullable=False, default=True)
    amount_bonus = Column(Integer, nullable=False)
    image = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(String, ForeignKey("enterprise.users.username"), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())
    updated_by = Column(String, ForeignKey("enterprise.users.username"), nullable=True)
    updated_date = Column(Date, nullable=False, default=date.today())
    
    filestable = relationship("DominoTablesFiles")
    
    def dict(self):
        return {
            "id": self.id,
            "tourney_id": self.tourney_id,
            "table_number": self.table_number,
            "is_smart": self.is_smart,
            "amount_bonus": self.amount_bonus,
            "is_active": self.is_active,
            'created_by': self.created_by
            }
        
class DominoTablesFiles(Base):
    """DominoTablesFiles Class contains standard information for  Files at dominos tables."""
 
    __tablename__ = "domino_tables_files"
    __table_args__ = {'schema' : 'events'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    table_id = Column(String, ForeignKey("events.domino_tables.id"), nullable=False)
    position = Column(Integer, nullable=False)
    is_ready = Column(Boolean, nullable=False, default=False)
    
    def dict(self):
        return {
            "id": self.id,
            "table_id": self.table_id,
            "position": self.position,
            "is_ready": self.is_ready
        }
