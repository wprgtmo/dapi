"""coding=utf-8."""

import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, Integer, Date, Text, Float
from ..config.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class Post(Base):
    """Post Class contains standard information for a Post."""
 
    __tablename__ = "post"
    __table_args__ = {'schema' : 'post'}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    image = Column(String(100), nullable=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String, nullable=False)
    created_by = Column(String, ForeignKey("enterprise.users.id"), nullable=False)
    created_date = Column(Date, nullable=False)
    publication_date = Column(Date, nullable=False)
    expire_date = Column(Date, nullable=True)
    updated_by = Column(String, ForeignKey("enterprise.users.id"), nullable=False)
    updated_date = Column(Date, nullable=False)
    status_id  = Column(Integer, ForeignKey("resources.entities_status.id"), nullable=False)
    
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "image": self.image,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "publication_date": self.publication_date,
            "expire_date": self.expite_date,
            "status_id": self.status_id
        }
