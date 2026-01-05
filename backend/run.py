#!/usr/bin/env python3
"""
Скрипт запуска VaultDoc API сервера
"""
import uvicorn
import sys

def main():
    """Запускаем FastAPI сервер"""
    print("🚀 Запускаем VaultDoc API сервер...")
    print(f"📁 Директория: {sys.path[0]}")
    print("🌐 API будет доступно по: http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    print("⏳ Для остановки нажмите Ctrl+C\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
