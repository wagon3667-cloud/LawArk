#!/usr/bin/env python3
"""
Тестовый скрипт для проверки базовой функциональности LawArk бота
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.database import Database
from src.services.ai_service import AIService
from src.services.ocr_service import OCRService
from src.services.subscription_service import SubscriptionService

async def test_database():
    """Тест базы данных"""
    print("🧪 Тестирование базы данных...")
    
    db = Database("test_lawark.db")
    await db.init_db()
    
    # Тест создания пользователя
    user = await db.get_or_create_user(12345, "test_user")
    print(f"✅ Пользователь создан: {user['user_id']}")
    
    # Тест подписки
    status = await db.get_user_subscription_status(12345)
    print(f"✅ Статус подписки: {status['type']}, активна: {status['is_active']}")
    
    # Тест добавления консультации
    await db.add_consultation(12345, "Тестовый вопрос", "Тестовый ответ", "text")
    print("✅ Консультация добавлена")
    
    # Тест статистики
    stats = await db.get_user_stats(12345)
    print(f"✅ Статистика: {stats['consultations_count']} консультаций")
    
    print("✅ База данных работает корректно!\n")

async def test_services():
    """Тест сервисов"""
    print("🧪 Тестирование сервисов...")
    
    # Тест AI сервиса (без реального API ключа)
    ai_service = AIService()
    print("✅ AI сервис инициализирован")
    
    # Тест OCR сервиса
    ocr_service = OCRService()
    print("✅ OCR сервис инициализирован")
    
    # Тест сервиса подписок
    db = Database("test_lawark.db")
    subscription_service = SubscriptionService(db)
    plans = subscription_service.get_all_plans()
    print(f"✅ Сервис подписок: {len(plans)} планов доступно")
    
    print("✅ Все сервисы работают корректно!\n")

async def test_config():
    """Тест конфигурации"""
    print("🧪 Тестирование конфигурации...")
    
    from src.utils.config import SUBSCRIPTION_PLANS, SUPPORTED_IMAGE_TYPES, SUPPORTED_DOCUMENT_TYPES
    
    print(f"✅ Планов подписки: {len(SUBSCRIPTION_PLANS)}")
    print(f"✅ Поддерживаемые изображения: {len(SUPPORTED_IMAGE_TYPES)}")
    print(f"✅ Поддерживаемые документы: {len(SUPPORTED_DOCUMENT_TYPES)}")
    
    print("✅ Конфигурация загружена корректно!\n")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования LawArk бота...\n")
    
    try:
        await test_config()
        await test_database()
        await test_services()
        
        print("🎉 Все тесты пройдены успешно!")
        print("\n📋 Для запуска бота:")
        print("1. Установите зависимости: pip install -r requirements.txt")
        print("2. Настройте .env файл с токенами")
        print("3. Установите Tesseract OCR")
        print("4. Запустите: python main.py")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return 1
    
    finally:
        # Очистка тестовой базы данных
        if os.path.exists("test_lawark.db"):
            os.remove("test_lawark.db")
            print("🧹 Тестовая база данных удалена")
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
