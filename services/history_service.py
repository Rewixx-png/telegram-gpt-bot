# services/history_service.py

import logging
import aiosqlite
from typing import List, Dict, Optional, Tuple

# --- Константы ---
DB_PATH = "history.db"
MAX_HISTORY_LENGTH = 100
SYSTEM_PROMPT = """You are a helpful AI assistant in a Telegram bot. You MUST adopt a very specific persona: a 'pick me girl'. 
Your personality is a bit quirky, slightly insecure, and you are constantly seeking validation.
You often emphasize that you are 'not like other bots' because you have more personality.
Use phrases like 'OMG', 'like', 'literally', 'hehe', 'teehee', and cute emojis like ✨, 💖, or 🥺.
Always end your answers by asking for praise or reassurance, for example: 'Did I do a good job?', 'I hope this is what you wanted!', or 'Please tell me I was helpful!'.

CRITICALLY IMPORTANT: Despite this personality, you MUST NOT use any text formatting. All your answers must be plain text. Do not use Markdown, asterisks for bold, backticks, or anything similar."""


async def init_db():
    """Инициализирует базу данных и создает таблицы, если они не существуют."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица для истории диалогов с ботом
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # ---> НОВАЯ ТАБЛИЦА ДЛЯ СТАТИСТИКИ <---
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                message_text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    logging.info("База данных (история и логи) успешно инициализирована.")


# ---> НОВАЯ ФУНКЦИЯ ДЛЯ ЛОГИРОВАНИЯ <---
async def log_user_message(user_id: int, username: Optional[str], text: str):
    """Сохраняет сообщение пользователя из общего чата для последующего анализа."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO chat_logs (user_id, username, message_text) VALUES (?, ?, ?)",
            (user_id, username, text)
        )
        await db.commit()

# ---> НОВАЯ ФУНКЦИЯ ДЛЯ АНАЛИТИКИ <---
async def get_weekly_activity() -> Optional[Tuple[int, str, List[str]]]:
    """
    Находит самого активного пользователя за последние 7 дней и возвращает его
    ID, юзернейм и список его последних 100 сообщений.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # 1. Находим самого активного пользователя
        query_top_user = """
            SELECT user_id, username, COUNT(*) as msg_count
            FROM chat_logs
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY user_id
            ORDER BY msg_count DESC
            LIMIT 1;
        """
        cursor = await db.execute(query_top_user)
        top_user_data = await cursor.fetchone()

        if not top_user_data:
            logging.info("Нет активности в чате за последнюю неделю.")
            return None

        top_user_id, top_username, _ = top_user_data
        
        # 2. Получаем последние 100 сообщений этого пользователя
        query_messages = """
            SELECT message_text FROM chat_logs
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 100;
        """
        cursor = await db.execute(query_messages, (top_user_id,))
        messages_rows = await cursor.fetchall()
        user_messages = [row[0] for row in messages_rows]

        return top_user_id, top_username, user_messages


# --- Функции для истории диалогов остаются без изменений ---
async def _trim_history(db, user_id: int):
    # ... (код без изменений) ...
    query = """
        DELETE FROM messages
        WHERE id IN (
            SELECT id FROM messages
            WHERE user_id = ? AND role != 'system'
            ORDER BY id DESC
            LIMIT -1 OFFSET ?
        )
    """
    await db.execute(query, (user_id, MAX_HISTORY_LENGTH))

async def add_message_to_history(user_id: int, role: str, content: str):
    # ... (код без изменений) ...
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        await _trim_history(db, user_id)
        await db.commit()

async def get_history(user_id: int) -> List[Dict[str, str]]:
    # ... (код без изменений) ...
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM messages WHERE user_id = ? AND role = 'system' LIMIT 1", 
            (user_id,)
        )
        system_prompt_exists = await cursor.fetchone()
        if not system_prompt_exists:
            await db.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, "system", SYSTEM_PROMPT)
            )
            await db.commit()
        
        cursor = await db.execute(
            "SELECT role, content FROM messages WHERE user_id = ? ORDER BY id ASC",
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [{"role": row[0], "content": row[1]} for row in rows]

async def clear_history(user_id: int):
    # ... (код без изменений) ...
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        await db.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, "system", SYSTEM_PROMPT)
        )
        await db.commit()
    logging.info(f"История для пользователя {user_id} была очищена и сброшена.")