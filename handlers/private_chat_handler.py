# handlers/private_chat_handler.py
import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from config_data.config import config
from services import gpt_service, history_service

router = Router()
router.message.filter(F.chat.type == "private", F.from_user.id == config.bot.admin_id)

@router.message(Command("reset"))
async def handle_reset_command(message: types.Message):
    """Обрабатывает команду /reset для очистки истории."""
    await history_service.clear_history(message.from_user.id)
    await message.answer("✅ Ваша история общения была очищена.")

@router.message(F.text)
async def handle_private_message_from_admin(message: types.Message):
    user_id = message.from_user.id
    user_prompt = message.text
    logging.info(f"Получен личный запрос от админа {user_id}: '{user_prompt}'")
    gpt_response = await gpt_service.get_gpt_response(user_id, user_prompt)
    if gpt_response:
        await message.answer(text=gpt_response)
    else:
        await message.answer("Произошла ошибка при обращении к нейросети. Попробуйте позже.")