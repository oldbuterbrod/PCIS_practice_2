"""
Модель прав доступа для папок и документов
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entity_type = Column(String(10), nullable=False)  # 'folder' или 'document'
    entity_id = Column(Integer, nullable=False)       # ID папки или документа
    can_view = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_manage_access = Column(Boolean, default=False)  # Может управлять правами других
    granted_by = Column(Integer, ForeignKey("users.id"))
    granted_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Permission(user_id={self.user_id}, entity={self.entity_type}:{self.entity_id})>"
