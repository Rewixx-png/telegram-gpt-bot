# bot.py

import asyncio
import logging
from aiogram import Bot, Dispatcher
# DefaultBotProperties больше не нужен, убираем его импорт
from config_data.config import config
from handlers import topic_handler, private_chat_handler
from services import history_service

async def main():
    """
    Основная функция для настройки и запуска бота.
    """
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Инициализируем базу данных
    logging.info("Инициализация базы данных истории...")
    await history_service.init_db()
    
    logging.info("Запуск бота...")

    # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
    # Инициализируем бота без настроек форматирования по умолчанию.
    # Теперь все сообщения будут отправляться как обычный текст.
    bot = Bot(token=config.bot.token)
    
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(topic_handler.router)
    dp.include_router(private_chat_handler.router)
    
    # Удаляем старые вебхуки
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")