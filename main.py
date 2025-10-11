import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.handlers import start, consultation, documents, payment
from src.database.database import Database
from src.utils.config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lawark.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    
    # Проверяем наличие токена
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        sys.exit(1)
    
    # Инициализируем бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Инициализируем диспетчер с хранилищем состояний
    dp = Dispatcher(storage=MemoryStorage())
    
    # Инициализируем базу данных
    db = Database()
    await db.init_db()
    logger.info("База данных инициализирована")
    
    # Регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(consultation.router)
    dp.include_router(documents.router)
    dp.include_router(payment.router)
    
    logger.info("Бот LawArk запущен")
    
    try:
        # Запускаем бота
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
