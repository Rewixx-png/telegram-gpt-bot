# services/gpt_service.py
import logging
from openai import AsyncOpenAI
from config_data.config import config
from services import history_service

client = AsyncOpenAI(api_key=config.gpt.api_key, base_url=config.gpt.base_url)

async def get_gpt_response(user_id: int, prompt: str) -> str | None:
    """
    Получает ответ от GPT, учитывая историю переписки с пользователем.
    Эта версия исправляет баг с порядком сообщений.
    """
    # 1. СНАЧАЛА получаем историю. Этот шаг гарантирует, что системный промпт
    # для пользователя уже создан в базе данных, если его там не было.
    messages_for_api = await history_service.get_history(user_id)
    
    # 2. ДОБАВЛЯЕМ текущий запрос пользователя прямо в список, который мы отправим в API.
    messages_for_api.append({"role": "user", "content": prompt})

    try:
        response_stream = await client.chat.completions.create(
            model=config.gpt.model,
            messages=messages_for_api,  # Отправляем в API уже обновленный список
            stream=True,
        )
        
        full_response = ""
        async for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
        
        if full_response:
            # 3. И только ТЕПЕРЬ, когда у нас есть и вопрос, и ответ,
            # мы сохраняем ОБА сообщения в базу данных для будущих диалогов.
            await history_service.add_message_to_history(user_id, "user", prompt)
            await history_service.add_message_to_history(user_id, "assistant", full_response)
            return full_response.strip()
        return None
    except Exception as e:
        logging.error(f"Ошибка при обработке стрима от OpenAI: {e}", exc_info=True)
        return None

async def generate_single_response(prompt: str) -> str | None:
    """
    Генерирует ответ от GPT на основе одного единственного промпта,
    не используя и не сохраняя историю.
    """
    try:
        response_stream = await client.chat.completions.create(
            model=config.gpt.model,
            messages=[{'role': 'user', 'content': prompt}],
            stream=True,
        )
        
        full_response = ""
        async for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
        
        return full_response.strip()

    except Exception as e:
        logging.error(f"Ошибка при генерации одиночного ответа от OpenAI: {e}", exc_info=True)
        return None