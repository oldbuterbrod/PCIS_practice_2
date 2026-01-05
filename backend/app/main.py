"""
Главный файл FastAPI приложения VaultDoc со ВСЕМИ эндпоинтами
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import engine, Base, get_db
from app.models.user import User
from app.models.folder import Folder
from app.models.document import Document
from app.models.permission import Permission
from app.models.comment import DocumentComment

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title="VaultDoc API",
    description="Корпоративный веб-сервис для управления документами - Курсовая работа РТУ МИРЭА",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Главная"])
async def root():
    """Корневая страница API"""
    return {
        "message": "✅ VaultDoc API успешно запущен!",
        "project": "Система управления документами",
        "author": "Студент РТУ МИРЭА",
        "status": "Сервер работает + БД подключена",
        "database": {
            "type": "PostgreSQL",
            "host": "localhost:5433",
            "tables": ["users", "folders", "documents", "permissions", "document_comments"]
        },
        "endpoints": {
            "documentation": "/docs",
            "health_check": "/health",
            "users_api": "/api/users",
            "folders_api": "/api/folders",
            "documents_api": "/api/documents",
            "permissions_api": "/api/permissions",
            "statistics": "/api/statistics"
        },
        "version": "1.0.0"
    }

@app.get("/health", tags=["Система"])
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "VaultDoc API",
        "database": "PostgreSQL (все таблицы созданы)"
    }

# ============ ПОЛЬЗОВАТЕЛИ ============

@app.get("/api/users", tags=["Пользователи"])
async def get_users(db: Session = Depends(get_db)):
    """Получить список пользователей ИЗ БАЗЫ ДАННЫХ"""
    try:
        users = db.query(User).all()
        
        return {
            "status": "success",
            "count": len(users),
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении пользователей: {str(e)}"
        )

@app.get("/api/users/{user_id}", tags=["Пользователи"])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получить пользователя по ID ИЗ БАЗЫ ДАННЫХ"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"Пользователь с ID {user_id} не найден"
            )
        
        return {
            "status": "success",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении пользователя: {str(e)}"
        )

@app.put("/api/users/{user_id}", tags=["Пользователи"])
async def update_user(
    user_id: int,
    full_name: str = None,
    role: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """Обновить пользователя"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"Пользователь с ID {user_id} не найден"
            )
        
        # Обновляем только переданные поля
        if full_name is not None:
            user.full_name = full_name
        if role is not None:
            if role not in ["admin", "manager", "accountant", "employee"]:
                raise HTTPException(
                    status_code=400,
                    detail="Некорректная роль. Допустимые значения: admin, manager, accountant, employee"
                )
            user.role = role
        if is_active is not None:
            user.is_active = is_active
        
        db.commit()
        db.refresh(user)
        
        return {
            "status": "success",
            "message": "Пользователь успешно обновлен",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении пользователя: {str(e)}"
        )

# ============ ПАПКИ ============

@app.get("/api/folders", tags=["Папки"])
async def get_folders(db: Session = Depends(get_db)):
    """Получить список папок ИЗ БАЗЫ ДАННЫХ"""
    try:
        folders = db.query(Folder).all()
        
        # Получаем имена владельцев
        folders_with_owners = []
        for folder in folders:
            owner = db.query(User).filter(User.id == folder.owner_id).first()
            folders_with_owners.append({
                "id": folder.id,
                "name": folder.name,
                "owner_id": folder.owner_id,
                "owner_name": owner.full_name if owner else "Неизвестно",
                "parent_id": folder.parent_id,
                "created_at": folder.created_at.isoformat() if folder.created_at else None,
                "updated_at": folder.updated_at.isoformat() if folder.updated_at else None
            })
        
        return {
            "status": "success",
            "count": len(folders),
            "folders": folders_with_owners
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении папок: {str(e)}"
        )

# ============ ДОКУМЕНТЫ ============

@app.get("/api/documents", tags=["Документы"])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Получить список документов ИЗ БАЗЫ ДАННЫХ"""
    try:
        query = db.query(Document)
        
        if status:
            query = query.filter(Document.status == status)
        
        documents = query.offset(skip).limit(limit).all()
        
        # Получаем дополнительную информацию
        documents_with_details = []
        for doc in documents:
            owner = db.query(User).filter(User.id == doc.owner_id).first()
            folder = db.query(Folder).filter(Folder.id == doc.folder_id).first() if doc.folder_id else None
            
            documents_with_details.append({
                "id": doc.id,
                "title": doc.title,
                "content_preview": doc.content[:100] + "..." if len(doc.content) > 100 else doc.content,
                "folder_id": doc.folder_id,
                "folder_name": folder.name if folder else None,
                "owner_id": doc.owner_id,
                "owner_name": owner.full_name if owner else None,
                "status": doc.status,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None
            })
        
        return {
            "status": "success",
            "count": len(documents),
            "skip": skip,
            "limit": limit,
            "documents": documents_with_details
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении документов: {str(e)}"
        )

@app.get("/api/documents/{document_id}", tags=["Документы"])
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Получить документ по ID ИЗ БАЗЫ ДАННЫХ"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Документ с ID {document_id} не найден"
            )
        
        owner = db.query(User).filter(User.id == document.owner_id).first()
        folder = db.query(Folder).filter(Folder.id == document.folder_id).first() if document.folder_id else None
        
        return {
            "status": "success",
            "document": {
                "id": document.id,
                "title": document.title,
                "content": document.content,
                "folder_id": document.folder_id,
                "folder_name": folder.name if folder else None,
                "owner_id": document.owner_id,
                "owner_name": owner.full_name if owner else None,
                "owner_role": owner.role if owner else None,
                "status": document.status,
                "created_at": document.created_at.isoformat() if document.created_at else None,
                "updated_at": document.updated_at.isoformat() if document.updated_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении документа: {str(e)}"
        )

@app.put("/api/documents/{document_id}", tags=["Документы"])
async def update_document(
    document_id: int,
    title: str = None,
    content: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Обновить документ"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Документ с ID {document_id} не найден"
            )
        
        # Обновляем только переданные поля
        if title is not None:
            document.title = title
        if content is not None:
            document.content = content
        if status is not None:
            if status not in ["draft", "under_review", "approved", "rejected"]:
                raise HTTPException(
                    status_code=400,
                    detail="Некорректный статус. Допустимые значения: draft, under_review, approved, rejected"
                )
            document.status = status
        
        document.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(document)
        
        return {
            "status": "success",
            "message": "Документ успешно обновлен",
            "document": {
                "id": document.id,
                "title": document.title,
                "status": document.status,
                "updated_at": document.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении документа: {str(e)}"
        )

# ============ КОММЕНТАРИИ ============

@app.get("/api/documents/{document_id}/comments", tags=["Комментарии"])
async def get_document_comments(document_id: int, db: Session = Depends(get_db)):
    """Получить комментарии к документу"""
    try:
        comments = db.query(DocumentComment).filter(
            DocumentComment.document_id == document_id
        ).order_by(DocumentComment.created_at.desc()).all()
        
        comments_with_authors = []
        for comment in comments:
            author = db.query(User).filter(User.id == comment.user_id).first()
            comments_with_authors.append({
                "id": comment.id,
                "comment": comment.comment,
                "user_id": comment.user_id,
                "author_name": author.full_name if author else "Неизвестно",
                "author_role": author.role if author else None,
                "created_at": comment.created_at.isoformat() if comment.created_at else None
            })
        
        return {
            "status": "success",
            "document_id": document_id,
            "count": len(comments),
            "comments": comments_with_authors
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении комментариев: {str(e)}"
        )

@app.post("/api/documents/{document_id}/comments", tags=["Комментарии"])
async def add_comment(
    document_id: int,
    comment: str,
    user_id: int = 1,  # Временно, потом заменим на текущего пользователя
    db: Session = Depends(get_db)
):
    """Добавить комментарий к документу"""
    try:
        # Проверяем что документ существует
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Документ с ID {document_id} не найден"
            )
        
        # Проверяем что пользователь существует
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"Пользователь с ID {user_id} не найден"
            )
        
        new_comment = DocumentComment(
            document_id=document_id,
            user_id=user_id,
            comment=comment
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        return {
            "status": "success",
            "message": "Комментарий успешно добавлен",
            "comment": {
                "id": new_comment.id,
                "document_id": new_comment.document_id,
                "comment": new_comment.comment,
                "author_name": user.full_name,
                "created_at": new_comment.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при добавлении комментария: {str(e)}"
        )

# ============ ПРАВА ДОСТУПА ============

@app.get("/api/permissions", tags=["Права доступа"])
async def get_permissions(
    user_id: int = None,
    entity_type: str = None,
    entity_id: int = None,
    db: Session = Depends(get_db)
):
    """Получить права доступа"""
    try:
        query = db.query(Permission)
        
        if user_id:
            query = query.filter(Permission.user_id == user_id)
        if entity_type:
            query = query.filter(Permission.entity_type == entity_type)
        if entity_id:
            query = query.filter(Permission.entity_id == entity_id)
        
        permissions = query.all()
        
        permissions_with_details = []
        for perm in permissions:
            user = db.query(User).filter(User.id == perm.user_id).first()
            granted_by = db.query(User).filter(User.id == perm.granted_by).first() if perm.granted_by else None
            
            permissions_with_details.append({
                "id": perm.id,
                "user_id": perm.user_id,
                "user_email": user.email if user else None,
                "user_name": user.full_name if user else None,
                "entity_type": perm.entity_type,
                "entity_id": perm.entity_id,
                "can_view": perm.can_view,
                "can_edit": perm.can_edit,
                "can_delete": perm.can_delete,
                "can_manage_access": perm.can_manage_access,
                "granted_by_id": perm.granted_by,
                "granted_by_name": granted_by.full_name if granted_by else None,
                "granted_at": perm.granted_at.isoformat() if perm.granted_at else None
            })
        
        return {
            "status": "success",
            "count": len(permissions),
            "permissions": permissions_with_details
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении прав доступа: {str(e)}"
        )

# ============ СТАТИСТИКА ============

@app.get("/api/statistics", tags=["Статистика"])
async def get_statistics(db: Session = Depends(get_db)):
    """Полная статистика системы"""
    try:
        user_count = db.query(User).count()
        folder_count = db.query(Folder).count()
        document_count = db.query(Document).count()
        permission_count = db.query(Permission).count()
        comment_count = db.query(DocumentComment).count()
        
        # Статистика по статусам документов
        status_stats = {}
        for status in ["draft", "under_review", "approved", "rejected"]:
            count = db.query(Document).filter(Document.status == status).count()
            status_stats[status] = count
        
        # Статистика по ролям пользователей
        role_stats = {}
        for role in ["admin", "manager", "employee"]:
            count = db.query(User).filter(User.role == role).count()
            if count > 0:
                role_stats[role] = count
        
        return {
            "status": "success",
            "statistics": {
                "users": {
                    "total": user_count,
                    "by_role": role_stats
                },
                "folders": folder_count,
                "documents": {
                    "total": document_count,
                    "by_status": status_stats
                },
                "permissions": permission_count,
                "comments": comment_count,
                "total_records": user_count + folder_count + document_count + permission_count + comment_count
            },
            "message": "Статистика системы VaultDoc"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )
