# services/scheduler_service.py

import logging
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config_data.config import config
from services import history_service, gpt_service

async def send_weekly_summary(bot: Bot):
    """
    Основная функция, которая выполняется по расписанию.
    Получает самого активного пользователя, генерирует о нем "факт" и отправляет в чат.
    """
    logging.info("🚀 Запуск еженедельной задачи: поиск самого активного пользователя...")
    
    # 1. Получаем данные из БД
    activity_data = await history_service.get_weekly_activity()
    
    if not activity_data:
        logging.info("Недостаточно данных для еженедельного отчета. Пропускаем.")
        return
        
    user_id, username, messages = activity_data
    
    # Если у пользователя нет юзернейма, делаем его упоминание через ID
    user_mention = f"@{username}" if username else f"пользователь с ID {user_id}"
    
    logging.info(f"Найден самый активный пользователь недели: {user_mention} (ID: {user_id})")

    # 2. Формируем промпт для GPT
    # Склеиваем все сообщения пользователя в один большой текст
    messages_text = "\n".join(messages)
    
    prompt = (
        f"Проанализируй этот набор сообщений от одного пользователя. "
        f"Его юзернейм в телеграме: {user_mention}. "
        f"Твоя задача — в очень короткой, забавной и немного 'подкольческой' манере (1-2 предложения) "
        f"сделать вывод о том, о чем этот человек чаще всего говорит или какая у него главная тема. "
        f"Обратись к нему напрямую. Например: 'Хей, {user_mention}, мы тут заметили, что ты просто одержим кошками!' "
        f"или 'Так-так, {user_mention}, кажется, кто-то не может перестать говорить о еде... 🍕'. "
        f"Будь креативным и дружелюбным. "
        f"ВАЖНО: Ответ должен быть ТОЛЬКО простым текстом без какого-либо форматирования. "
        f"Вот сообщения для анализа:\n\n{messages_text}"
    )

    # 3. Генерируем "подкол"
    summary_text = await gpt_service.generate_single_response(prompt)
    
    if summary_text:
        try:
            # 4. Отправляем сообщение в чат
            await bot.send_message(
                chat_id=config.settings.allowed_chat_id,
                text=f"🏆 Подводим итоги активности за неделю! 🏆\n\n{summary_text}"
            )
            logging.info(f"Еженедельный 'подкол' для {user_mention} успешно отправлен.")
        except Exception as e:
            logging.error(f"Не удалось отправить еженедельный отчет в чат: {e}")
    else:
        logging.warning("Не удалось сгенерировать текст для еженедельного отчета.")


def setup_scheduler(bot: Bot):
    """Настраивает и запускает планировщик задач."""
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow") # Можешь указать свой часовой пояс
    
    # Добавляем нашу задачу, которая будет выполняться каждую неделю в воскресенье в 19:00
    scheduler.add_job(
        send_weekly_summary, 
        trigger='cron', 
        day_of_week='sun', 
        hour=19, 
        minute=0,
        kwargs={'bot': bot}
    )
    
    scheduler.start()
    logging.info("Планировщик еженедельных задач запущен.")