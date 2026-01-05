"""
Скрипт для добавления тестовых данных для Permission и Comment
"""
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.folder import Folder
from app.models.document import Document
from app.models.permission import Permission
from app.models.comment import DocumentComment
from datetime import datetime, timedelta

def add_permissions_and_comments():
    """Добавление прав доступа и комментариев"""
    db = SessionLocal()
    
    try:
        print("🔄 Создаем таблицы для Permission и Comment...")
        Base.metadata.create_all(bind=engine)
        
        # Получаем существующих пользователей
        admin = db.query(User).filter(User.email == "admin@vaultdoc.ru").first()
        manager = db.query(User).filter(User.email == "manager@vaultdoc.ru").first()
        employee = db.query(User).filter(User.email == "employee@vaultdoc.ru").first()
        
        print("🔐 Добавляем права доступа...")
        
        # Права на папки
        folder_permissions = [
            # Даем менеджеру доступ к папке "Проекты"
            Permission(
                user_id=manager.id,
                entity_type="folder",
                entity_id=3,  # Папка "Проекты"
                can_view=True,
                can_edit=True,
                can_delete=False,
                can_manage_access=False,
                granted_by=admin.id
            ),
            # Даем сотруднику доступ к общей папке
            Permission(
                user_id=employee.id,
                entity_type="folder",
                entity_id=1,  # Папка "Общие документы"
                can_view=True,
                can_edit=False,
                can_delete=False,
                can_manage_access=False,
                granted_by=admin.id
            )
        ]
        
        for perm in folder_permissions:
            db.add(perm)
        
        # Права на документы
        document_permissions = [
            # Менеджер может редактировать документ в проектах
            Permission(
                user_id=manager.id,
                entity_type="document",
                entity_id=4,  # Документ "Техническое задание проекта 'Альфа'"
                can_view=True,
                can_edit=True,
                can_delete=False,
                granted_by=admin.id
            ),
            # Сотрудник может просматривать правила
            Permission(
                user_id=employee.id,
                entity_type="document",
                entity_id=1,  # Документ "Правила внутреннего распорядка"
                can_view=True,
                can_edit=False,
                can_delete=False,
                granted_by=admin.id
            )
        ]
        
        for perm in document_permissions:
            db.add(perm)
        
        print("💬 Добавляем комментарии...")
        
        # Комментарии к документам
        comments = [
            DocumentComment(
                document_id=4,  # Техническое задание
                user_id=manager.id,
                comment="Нужно добавить раздел по бюджету",
                created_at=datetime.now() - timedelta(days=4)
            ),
            DocumentComment(
                document_id=4,
                user_id=admin.id,
                comment="Согласен, добавьте пожалуйста",
                created_at=datetime.now() - timedelta(days=3)
            ),
            DocumentComment(
                document_id=3,  # Финансовый план
                user_id=admin.id,
                comment="Отличный план! Когда будет готов окончательный вариант?",
                created_at=datetime.now() - timedelta(days=2)
            ),
            DocumentComment(
                document_id=3,
                user_id=employee.id,
                comment="Будет готов к концу недели",
                created_at=datetime.now() - timedelta(days=1)
            )
        ]
        
        for comment in comments:
            db.add(comment)
        
        db.commit()
        
        print("✅ Добавлено:")
        print(f"   🔐 Прав доступа: {len(folder_permissions) + len(document_permissions)}")
        print(f"   💬 Комментариев: {len(comments)}")
        
        # Статистика
        perm_count = db.query(Permission).count()
        comment_count = db.query(DocumentComment).count()
        
        print(f"\n📊 Всего в системе:")
        print(f"   👥 Пользователей: {db.query(User).count()}")
        print(f"   📁 Папок: {db.query(Folder).count()}")
        print(f"   📄 Документов: {db.query(Document).count()}")
        print(f"   🔐 Прав доступа: {perm_count}")
        print(f"   💬 Комментариев: {comment_count}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_permissions_and_comments()
