# config_data/config.py
# Вся конфигурация теперь читается из переменных окружения.
# Это, блядь, правильно для работы с Docker.

import os
from dataclasses import dataclass

@dataclass
class BotConfig:
    token: str
    admin_id: int

@dataclass
class GptConfig:
    api_key: str
    tavily_api_key: str # Добавили ключ для Tavily
    base_url: str
    model: str
    system_prompt: str # Добавили системный промпт

@dataclass
class Settings:
    allowed_chat_id: int

@dataclass
class Config:
    bot: BotConfig
    gpt: GptConfig
    settings: Settings

def load_config():
    """
    Загружает конфигурацию из переменных окружения.
    """
    # Проверяем, что все переменные на месте, иначе нахуй падаем с ошибкой.
    required_vars = [
        'TELEGRAM_BOT_TOKEN', 'ADMIN_ID', 'OPENAI_API_KEY', 
        'TAVILY_API_KEY', 'ALLOWED_CHAT_ID', 'SYSTEM_PROMPT'
    ]
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Ебаный в рот, переменная окружения {var} не установлена!")

    return Config(
        bot=BotConfig(
            token=os.getenv('TELEGRAM_BOT_TOKEN'),
            admin_id=int(os.getenv('ADMIN_ID'))
        ),
        gpt=GptConfig(
            api_key=os.getenv('OPENAI_API_KEY'),
            tavily_api_key=os.getenv('TAVILY_API_KEY'),
            base_url=os.getenv('OPENAI_BASE_URL', "https://api.openai.com/v1"),
            model=os.getenv('GPT_MODEL', "gpt-4o-mini"),
            system_prompt=os.getenv('SYSTEM_PROMPT')
        ),
        settings=Settings(
            allowed_chat_id=int(os.getenv('ALLOWED_CHAT_ID'))
        )
    )

# Загружаем конфиг сразу при импорте, чтобы был доступен во всем проекте.
config = load_config()