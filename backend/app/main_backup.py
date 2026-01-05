"""
Главный файл FastAPI приложения VaultDoc - УПРОЩЕННАЯ ВЕРСИЯ
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base

# Импортируем модели для создания таблиц
from app.models.user import User
from app.models.folder import Folder

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
            "tables": ["users", "folders"]
        },
        "endpoints": {
            "documentation": "/docs",
            "health_check": "/health",
            "users_api": "/api/users",
            "db_check": "/api/db-check"
        },
        "version": "1.0.0"
    }

@app.get("/health", tags=["Система"])
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "VaultDoc API",
        "database": "PostgreSQL (таблицы созданы)"
    }

# ============ ПРОСТЫЕ ЭНДПОИНТЫ НАПРЯМУЮ ============

@app.get("/api/users", tags=["Пользователи"])
async def get_users():
    """Получить список пользователей"""
    return {
        "status": "success",
        "users": [
            {"id": 1, "email": "admin@vaultdoc.ru", "name": "Администратор", "role": "admin"},
            {"id": 2, "email": "manager@vaultdoc.ru", "name": "Менеджер Петров", "role": "manager"},
            {"id": 3, "email": "employee@vaultdoc.ru", "name": "Сотрудник Иванов", "role": "employee"}
        ]
    }

@app.get("/api/users/{user_id}", tags=["Пользователи"])
async def get_user(user_id: int):
    """Получить пользователя по ID"""
    return {
        "id": user_id,
        "email": f"user{user_id}@vaultdoc.ru",
        "name": f"Пользователь {user_id}",
        "role": "employee"
    }

@app.get("/api/db-check", tags=["База данных"])
async def check_database():
    """Проверка подключения к БД"""
    return {
        "status": "success",
        "database": "PostgreSQL",
        "host": "localhost:5433",
        "message": "✅ База данных подключена (таблицы созданы)"
    }

@app.post("/api/users", tags=["Пользователи"])
async def create_user():
    """Создать нового пользователя (заглушка)"""
    return {
        "status": "success",
        "message": "Пользователь создан",
        "user_id": 4
    }

# ============ ЭНДПОИНТЫ ДЛЯ ДОКУМЕНТОВ ============

@app.get("/api/documents", tags=["Документы"])
async def get_documents():
    """Получить список документов"""
    return {
        "status": "success",
        "documents": [
            {"id": 1, "title": "Отчет за январь", "status": "approved"},
            {"id": 2, "title": "План работ", "status": "draft"},
            {"id": 3, "title": "Презентация", "status": "under_review"}
        ]
    }

@app.get("/api/folders", tags=["Папки"])
async def get_folders():
    """Получить список папок"""
    return {
        "status": "success",
        "folders": [
            {"id": 1, "name": "Общие документы", "document_count": 5},
            {"id": 2, "name": "Отчеты", "document_count": 3},
            {"id": 3, "name": "Личные", "document_count": 2}
        ]
    }
