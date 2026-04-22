#!/usr/bin/env python3
"""
Точка входа в бота Factura Beauty Boutique
"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TELEGRAM_BOT_TOKEN, validate_config, logger
from handlers import router

async def main():
    """Основная функция запуска бота"""
    
    # Проверяем конфигурацию
    if not validate_config():
        logger.error("Неверная конфигурация. Завершение работы.")
        return
    
    logger.info("Запуск бота Factura Beauty Boutique")
    
    # Инициализация бота и диспетчера
    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    dp = Dispatcher()
    
    # Подключаем роутер с обработчиками
    dp.include_router(router)
    
    # Удаляем старые вебхуки и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("Бот успешно запущен и готов к работе")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске поллинга: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)