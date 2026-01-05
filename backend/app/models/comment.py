"""
Модель комментария к документам
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class DocumentComment(Base):
    __tablename__ = "document_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Comment(id={self.id}, document_id={self.document_id})>"
