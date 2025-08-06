# services/gpt_service.py

import logging
from openai import AsyncOpenAI
from config_data.config import config

# Инициализируем клиент один раз при старте
client = AsyncOpenAI(
    api_key=config.gpt.api_key,
    base_url=config.gpt.base_url
)

async def get_gpt_response(prompt: str) -> str | None:
    """
    Отправляет запрос к GPT и возвращает текстовый ответ.
    В случае ошибки возвращает None.
    """
    try:
        response_stream = await client.chat.completions.create(
            model=config.gpt.model,
            messages=[{'role': 'user', 'content': prompt}],
            stream=True,
        )
        
        full_response = ""
        async for chunk in response_stream:
            # ---> ВОТ ИСПРАВЛЕНИЕ <---
            # Сначала проверяем, что список choices не пустой,
            # и только потом обращаемся к его первому элементу.
            if chunk.choices and chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
        
        return full_response.strip()

    except Exception as e:
        # Теперь мы будем видеть в логах более точную ошибку, если она повторится
        logging.error(f"Ошибка при обработке стрима от OpenAI: {e}", exc_info=True)
        return None