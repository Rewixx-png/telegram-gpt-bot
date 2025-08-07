# bot.py

import asyncio
import logging
from aiogram import Bot, Dispatcher
from config_data.config import config

# Импортируем наши модули
from handlers import topic_handler, private_chat_handler, group_events_handler
from services import history_service, scheduler_service

async def main():
    """
    Основная функция для настройки и запуска бота.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    logging.info("Инициализация базы данных...")
    await history_service.init_db()
    
    logging.info("Запуск бота...")

    bot = Bot(token=config.bot.token)
    dp = Dispatcher()

    # --- Подключаем роутеры ---
    # Важно: log_router должен идти первым, чтобы он ловил все сообщения до того,
    # как их могут перехватить другие хендлеры и остановить обработку.
    dp.include_router(topic_handler.log_router)
    
    dp.include_router(topic_handler.router)
    dp.include_router(private_chat_handler.router)
    dp.include_router(group_events_handler.router)
    
    # --- Запускаем планировщик ---
    scheduler_service.setup_scheduler(bot)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")