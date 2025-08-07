# handlers/group_events_handler.py

import logging
from aiogram import Router, F, types
from config_data.config import config
# Импортируем нашу новую функцию из сервиса
from services.gpt_service import generate_single_response

router = Router()

# Фильтруем события: только в разрешенном чате
router.message.filter(F.chat.id == config.settings.allowed_chat_id)

@router.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    """
    Этот хендлер срабатывает, когда в чат добавляется новый участник.
    """
    # message.new_chat_members - это список, т.к. можно добавить сразу несколько человек
    for member in message.new_chat_members:
        user_name = member.first_name
        logging.info(f"В чат вошел новый пользователь: {user_name} (ID: {member.id})")

        # Создаем креативный промпт для GPT
        prompt = (
            f"В наш Telegram-чат только что вошел новый участник по имени {user_name}. "
            f"Придумай для него короткое (2-3 предложения), очень дружелюбное, забавное и немного 'своеское' приветствие от лица всего нашего сообщества. "
            f"Заставь его почувствовать себя как дома. Можешь использовать смайлики."
            f"ВАЖНО: Ответ должен быть ТОЛЬКО простым текстом без какого-либо форматирования."
        )

        # Генерируем приветствие
        welcome_text = await generate_single_response(prompt)

        if welcome_text:
            # Отправляем сгенерированный текст в чат.
            # message.answer ответит на сервисное сообщение о входе,
            # что будет выглядеть как обычное сообщение в чате.
            await message.answer(welcome_text)
            logging.info(f"Сгенерировано и отправлено приветствие для {user_name}.")
        else:
            # Если GPT не ответил, отправим стандартное приветствие
            await message.answer(f"Привет, {user_name}! Добро пожаловать в наш чат! 👋")
            logging.warning("Не удалось сгенерировать приветствие от GPT, отправлено стандартное.")