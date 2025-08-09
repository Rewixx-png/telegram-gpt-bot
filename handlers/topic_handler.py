# handlers/topic_handler.py

import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from config_data.config import config
from services import gpt_service, history_service

# --- Роутер для ответов на обращения к боту ---
router = Router()
router.message.filter(F.chat.id == config.settings.allowed_chat_id)

@router.message(Command("reset"))
async def handle_reset_command_in_topic(message: types.Message):
    """Обрабатывает команду /reset в группе."""
    await history_service.clear_history(message.from_user.id)
    await message.reply("✅ Ваша личная история общения с ботом была очищена.")

@router.message(F.text)
async def handle_topic_message(message: types.Message):
    """
    Обрабатывает сообщения в разрешенном чате, но отвечает только
    если сообщение является реплаем на сообщение бота или содержит его тег.
    """
    bot_info = await message.bot.get_me()
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id
    is_mention_to_bot = message.text and f"@{bot_info.username}" in message.text
    
    if not is_reply_to_bot and not is_mention_to_bot:
        return

    user_id = message.from_user.id
    user_prompt = message.text.replace(f"@{bot_info.username}", "").strip()
    
    logging.info(f"Запрос к боту от {user_id} в топике: '{user_prompt}'")
    
    # Получаем ответ и, возможно, путь к файлу
    text_response, file_to_send = await gpt_service.get_gpt_response(user_id, user_prompt)
    
    if file_to_send:
        try:
            # Отправляем фото в ответ на сообщение
            photo = FSInputFile(file_to_send)
            await message.reply_photo(photo, caption=text_response or "Скриншот готов.")
        except Exception as e:
            logging.error(f"Не удалось отправить файл {file_to_send}: {e}")
            await message.reply("Не смог отправить скриншот, похоже, файл не найден или что-то сломалось.")
    elif text_response:
        # Отправляем обычный текстовый ответ
        await message.reply(text=text_response)
    else:
        # Сообщаем об ошибке
        await message.reply("Произошла ошибка при обращении к нейросети.")


# --- Новый роутер для логирования всех сообщений в чате ---
log_router = Router()
log_router.message.filter(F.chat.id == config.settings.allowed_chat_id)

@log_router.message(F.text)
async def log_all_messages(message: types.Message):
    """
    Этот хендлер ловит АБСОЛЮТНО все текстовые сообщения в чате
    и сохраняет их в базу данных для статистики.
    Он не отвечает пользователю.
    """
    bot_info = await message.bot.get_me()
    if message.from_user.id == bot_info.id:
        return

    await history_service.log_user_message(
        user_id=message.from_user.id,
        username=message.from_user.username,
        text=message.text
    )