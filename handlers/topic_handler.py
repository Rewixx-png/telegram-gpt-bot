# handlers/topic_handler.py
import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from config_data.config import config
from services import gpt_service, history_service

router = Router()
router.message.filter(F.chat.id == config.settings.allowed_chat_id)

@router.message(Command("reset"))
async def handle_reset_command_in_topic(message: types.Message):
    """Обрабатывает команду /reset в группе."""
    await history_service.clear_history(message.from_user.id)
    await message.reply("✅ Ваша личная история общения с ботом была очищена.")

@router.message(F.text)
async def handle_topic_message(message: types.Message):
    bot_info = await message.bot.get_me()
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id
    is_mention_to_bot = message.text and f"@{bot_info.username}" in message.text
    if not is_reply_to_bot and not is_mention_to_bot:
        return

    user_id = message.from_user.id
    user_prompt = message.text.replace(f"@{bot_info.username}", "").strip()
    logging.info(f"Запрос к боту от {user_id} в топике: '{user_prompt}'")
    gpt_response = await gpt_service.get_gpt_response(user_id, user_prompt)
    if gpt_response:
        await message.reply(text=gpt_response)
    else:
        await message.reply("Произошла ошибка при обращении к нейросети.")