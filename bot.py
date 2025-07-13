import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import start, status

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 Запуск бота...")
    if BOT_TOKEN:
        logger.info(f"Токен бота: {BOT_TOKEN[:10]}...")
    else:
        logger.error("❌ Токен бота не найден!")
        return
    
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(status.router)
    
    logger.info("📡 Подключаемся к Telegram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())