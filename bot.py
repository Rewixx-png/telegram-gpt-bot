# bot.py

import asyncio
import logging
from aiogram import Bot, Dispatcher
# Импортируем новый класс для настроек по умолчанию
from aiogram.client.default import DefaultBotProperties
from config_data.config import config
from handlers import topic_handler, private_chat_handler

async def main():
    """
    Основная функция для настройки и запуска бота.
    """
    # Настройка логирования для вывода информации о работе бота в консоль
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.info("Запуск бота...")

    # Инициализация Бота и Диспетчера
    # Инициализируем бота по-новому, используя DefaultBotProperties
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    # Подключаем роутеры из наших модулей-обработчиков
    # Роутер для обработки сообщений в группе с топиками
    dp.include_router(topic_handler.router)
    # Роутер для обработки личных сообщений от админа
    dp.include_router(private_chat_handler.router)
    
    # Удаляем старые вебхуки, которые могли остаться от предыдущих запусков
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем long polling для получения обновлений от Telegram
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        # Запускаем асинхронную функцию main
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Обрабатываем чистое завершение работы (Ctrl+C)
        logging.info("Бот остановлен.")