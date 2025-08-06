# services/gpt_service.py
import logging
from openai import AsyncOpenAI
from config_data.config import config
from services import history_service

client = AsyncOpenAI(api_key=config.gpt.api_key, base_url=config.gpt.base_url)

async def get_gpt_response(user_id: int, prompt: str) -> str | None:
    # 1. Добавляем текущий запрос (теперь асинхронно)
    await history_service.add_message_to_history(user_id, "user", prompt)

    # 2. Получаем всю историю (теперь асинхронно)
    messages_for_api = await history_service.get_history(user_id)

    try:
        response_stream = await client.chat.completions.create(
            model=config.gpt.model,
            messages=messages_for_api,
            stream=True,
        )
        
        full_response = ""
        async for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
        
        if full_response:
            # 3. Добавляем ответ в историю (теперь асинхронно)
            await history_service.add_message_to_history(user_id, "assistant", full_response)
            return full_response.strip()
        return None
    except Exception as e:
        logging.error(f"Ошибка при обработке стрима от OpenAI: {e}", exc_info=True)
        return None