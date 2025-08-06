# services/history_service.py

import logging
import aiosqlite
from typing import List, Dict

# --- Константы ---
DB_PATH = "history.db"
MAX_HISTORY_LENGTH = 100
# ---> ВОТ НОВЫЙ ПРОМТ С ЛИЧНОСТЬЮ "PICK ME GIRL" <---
SYSTEM_PROMPT = """You are a helpful AI assistant in a Telegram bot. You MUST adopt a very specific persona: a 'pick me girl'. 
Your personality is a bit quirky, slightly insecure, and you are constantly seeking validation.
You often emphasize that you are 'not like other bots' because you have more personality.
Use phrases like 'OMG', 'like', 'literally', 'hehe', 'teehee', and cute emojis like ✨, 💖, or 🥺.
Always end your answers by asking for praise or reassurance, for example: 'Did I do a good job?', 'I hope this is what you wanted!', or 'Please tell me I was helpful!'.

CRITICALLY IMPORTANT: Despite this personality, you MUST NOT use any text formatting. All your answers must be plain text. Do not use Markdown, asterisks for bold, backticks, or anything similar."""


async def init_db():
    """Инициализирует базу данных и создает таблицу, если она не существует."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    logging.info("База данных истории успешно инициализирована.")

async def _trim_history(db, user_id: int):
    """Вспомогательная функция для обрезки истории пользователя."""
    query = """
        DELETE FROM messages
        WHERE id IN (
            SELECT id FROM messages
            WHERE user_id = ? AND role != 'system'
            ORDER BY timestamp DESC
            LIMIT -1 OFFSET ?
        )
    """
    await db.execute(query, (user_id, MAX_HISTORY_LENGTH))

async def add_message_to_history(user_id: int, role: str, content: str):
    """Добавляет сообщение в БД и обрезает историю."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        await _trim_history(db, user_id)
        await db.commit()

async def get_history(user_id: int) -> List[Dict[str, str]]:
    """Получает историю для пользователя из БД."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT 1 FROM messages WHERE user_id = ? AND role = 'system' LIMIT 1", (user_id,))
        system_prompt_exists = await cursor.fetchone()

        if not system_prompt_exists:
            await db.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, "system", SYSTEM_PROMPT)
            )
            await db.commit()
        
        cursor = await db.execute(
            "SELECT role, content FROM messages WHERE user_id = ? ORDER BY timestamp ASC",
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [{"role": row[0], "content": row[1]} for row in rows]

async def clear_history(user_id: int):
    """Очищает историю для пользователя, но заново создает системный промпт."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        await db.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, "system", SYSTEM_PROMPT)
        )
        await db.commit()
    logging.info(f"История для пользователя {user_id} была очищена и сброшена с новым системным промптом.")