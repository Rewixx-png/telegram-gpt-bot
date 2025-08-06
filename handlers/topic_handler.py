# handlers/topic_handler.py

import logging
from aiogram import Router, F, types
from config_data.config import config
from services.gpt_service import get_gpt_response

# Создаем роутер для этого модуля
router = Router()

# Фильтруем сообщения: только из разрешенного чата и только текстовые
router.message.filter(F.chat.id == config.settings.allowed_chat_id, F.text)

@router.message()
async def handle_topic_message(message: types.Message):
    """
    Обрабатывает сообщения в разрешенном чате, отправляет их в GPT
    и возвращает ответ в тот же топик.
    """
    # Мы по-прежнему получаем thread_id, на случай если он понадобится для чего-то еще
    thread_id = message.message_thread_id
    user_prompt = message.text

    logging.info(f"Запрос в топике {thread_id}: '{user_prompt}'")
    
    # Получаем ответ от GPT через наш сервис
    gpt_response = await get_gpt_response(user_prompt)

    if gpt_response:
        # ---> ВОТ ИСПРАВЛЕНИЕ <---
        # Просто используем reply без лишних параметров.
        # Aiogram сам поймет, что нужно ответить в тот же топик.
        await message.reply(text=gpt_response)
        logging.info("Ответ от GPT успешно отправлен.")
    else:
        # Для сообщений об ошибках поступаем так же.
        error_message = "Произошла ошибка при обращении к нейросети. Попробуйте позже."
        await message.reply(text=error_message)
        logging.warning("Не удалось получить ответ от GPT.")