"""
Скрипт для добавления тестовых данных в БД
"""
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.folder import Folder
from app.models.document import Document
from datetime import datetime
import hashlib

# Создаем таблицы
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Проверяем, есть ли уже пользователи
    user_count = db.query(User).count()
    
    if user_count == 0:
        print("Добавляем тестовых пользователей...")
        
        # Создаем тестовых пользователей
        users = [
            User(
                email="admin@vaultdoc.ru",
                password_hash=hashlib.sha256(b"admin123").hexdigest(),
                full_name="Администратор Системы",
                role="admin",
                is_active=True
            ),
            User(
                email="manager@vaultdoc.ru",
                password_hash=hashlib.sha256(b"manager123").hexdigest(),
                full_name="Петров Петр Иванович",
                role="manager",
                is_active=True
            ),
            User(
                email="employee@vaultdoc.ru",
                password_hash=hashlib.sha256(b"employee123").hexdigest(),
                full_name="Сидорова Анна Михайловна",
                role="employee",
                is_active=True
            )
        ]
        
        for user in users:
            db.add(user)
        
        db.commit()
        
        # Получаем ID созданных пользователей
        admin = db.query(User).filter(User.email == "admin@vaultdoc.ru").first()
        manager = db.query(User).filter(User.email == "manager@vaultdoc.ru").first()
        employee = db.query(User).filter(User.email == "employee@vaultdoc.ru").first()
        
        print("Добавляем тестовые папки...")
        
        # Создаем тестовые папки
        folders = [
            Folder(
                name="Общие документы",
                owner_id=admin.id,
                parent_id=None
            ),
            Folder(
                name="Отчеты",
                owner_id=admin.id,
                parent_id=None
            ),
            Folder(
                name="Проекты",
                owner_id=manager.id,
                parent_id=None
            ),
            Folder(
                name="2024",
                owner_id=admin.id,
                parent_id=2  # Подпапка "Отчеты"
            )
        ]
        
        for folder in folders:
            db.add(folder)
        
        db.commit()
        
        print("Добавляем тестовые документы...")
        
        # Создаем тестовые документы
        documents = [
            Document(
                title="Добро пожаловать в VaultDoc!",
                content="Это система управления документами компании. Здесь вы можете создавать, редактировать и совместно работать над документами.",
                folder_id=1,  # Общие документы
                owner_id=admin.id,
                status="approved"
            ),
            Document(
                title="Правила работы с документами",
                content="1. Все важные документы должны быть утверждены руководителем.\n2. Не удаляйте документы без согласования.\n3. Используйте комментарии для обсуждения изменений.",
                folder_id=1,  # Общие документы
                owner_id=admin.id,
                status="approved"
            ),
            Document(
                title="Отчет за январь 2024",
                content="В январе мы выполнили все поставленные задачи. Прибыль составила 1.2 млн рублей.",
                folder_id=4,  # 2024 (в папке Отчеты)
                owner_id=manager.id,
                status="under_review"
            ),
            Document(
                title="План работ на февраль",
                content="Основные задачи на февраль:\n1. Запуск нового проекта\n2. Обновление оборудования\n3. Обучение сотрудников",
                folder_id=3,  # Проекты
                owner_id=employee.id,
                status="draft"
            ),
            Document(
                title="Мои заметки",
                content="Не забыть:\n- Подготовить презентацию\n- Созвон с клиентом в 15:00\n- Отправить отчет бухгалтерии",
                folder_id=None,  # Без папки
                owner_id=employee.id,
                status="draft"
            )
        ]
        
        for document in documents:
            db.add(document)
        
        db.commit()
        
        print(f"✅ Добавлено: {len(users)} пользователей, {len(folders)} папок, {len(documents)} документов")
        print("👤 Пользователи:")
        for user in db.query(User).all():
            print(f"  - {user.email} ({user.role})")
        
        print("\n📁 Папки:")
        for folder in db.query(Folder).all():
            owner = db.query(User).filter(User.id == folder.owner_id).first()
            print(f"  - {folder.name} (владелец: {owner.full_name if owner else '?'})")
            
    else:
        print(f"ℹ️ В БД уже есть {user_count} пользователей")
        
except Exception as e:
    db.rollback()
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
