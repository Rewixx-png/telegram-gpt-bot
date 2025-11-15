# handlers/private_chat_handler.py
from loguru import logger
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
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
    logger.info(f"Получен личный запрос от админа {user_id}: '{user_prompt}'")
    
    # Получаем ответ и, возможно, путь к файлу
    text_response, file_to_send = await gpt_service.get_gpt_response(user_id, user_prompt)

    if file_to_send:
        try:
            # Отправляем фото
            photo = FSInputFile(file_to_send)
            await message.answer_photo(photo, caption=text_response or "Скриншот готов.")
        except Exception as e:
            logger.error(f"Не удалось отправить файл {file_to_send}: {e}")
            await message.answer("Не смог отправить скриншот, похоже, файл не найден или что-то сломалось.")
    elif text_response:
        # Отправляем обычный текстовый ответ
        await message.answer(text=text_response)
    else:
        # Сообщаем об ошибке
        await message.answer("Произошла ошибка при обращении к нейросети. Попробуйте позже.")