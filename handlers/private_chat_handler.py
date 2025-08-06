# handlers/private_chat_handler.py

import logging
from aiogram import Router, F, types
from config_data.config import config
from services.gpt_service import get_gpt_response

# Создаем новый роутер специально для этого модуля
router = Router()

# Фильтруем сообщения:
# 1. Это личный чат (F.chat.type == "private")
# 2. ID пользователя совпадает с admin_id из конфига
# 3. Сообщение является текстом
router.message.filter(
    F.chat.type == "private",
    F.from_user.id == config.bot.admin_id
)

@router.message(F.text)
async def handle_private_message_from_admin(message: types.Message):
    """
    Обрабатывает личные сообщения от админа, отправляет их в GPT
    и возвращает ответ.
    """
    user_prompt = message.text

    logging.info(f"Получен личный запрос от админа: '{user_prompt}'")

    # Используем тот же сервис для получения ответа от GPT
    gpt_response = await get_gpt_response(user_prompt)

    if gpt_response:
        # message.answer - удобный шорткат для ответа в тот же чат
        await message.answer(text=gpt_response)
        logging.info("Ответ админу успешно отправлен.")
    else:
        # Если сервис вернул None, значит была ошибка
        error_message = "Произошла ошибка при обращении к нейросети. Попробуйте позже."
        await message.answer(text=error_message)
        logging.warning("Не удалось получить ответ от GPT для админа.")