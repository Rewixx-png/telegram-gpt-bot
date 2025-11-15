# services/history_service.py

import aiosqlite
from loguru import logger
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from config_data.config import config # <-- Импортируем наш конфиг

# ---> ПУТЬ К БД ТЕПЕРЬ ВЕДЕТ В ПАПКУ data <---
DB_PATH = "data/history.db"
MAX_HISTORY_LENGTH = 20

def get_system_prompt() -> str:
    """
    Создает системный промт, вставляя в него актуальную дату.
    Промпт теперь берется из конфига, а не захардкожен.
    """
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    return config.gpt.system_prompt.format(current_date=current_date_str)


# Остальной код файла остается БЕЗ ИЗМЕНЕНИЙ.
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db: await db.executescript(""" CREATE TABLE IF NOT EXISTS messages ( id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP ); CREATE TABLE IF NOT EXISTS chat_logs ( id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, username TEXT, message_text TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP ); """)
    logger.info("База данных (история и логи) успешно инициализирована.")
async def log_user_message(user_id: int, username: Optional[str], text: str):
    async with aiosqlite.connect(DB_PATH) as db: await db.execute( "INSERT INTO chat_logs (user_id, username, message_text) VALUES (?, ?, ?)", (user_id, username, text) ); await db.commit()
async def get_weekly_activity() -> Optional[Tuple[int, str, List[str]]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id, username, COUNT(*) as msg_count FROM chat_logs WHERE timestamp >= datetime('now', '-7 days') GROUP BY user_id ORDER BY msg_count DESC LIMIT 1;")
        top_user_data = await cursor.fetchone()
        if not top_user_data: return None
        top_user_id, top_username, _ = top_user_data
        cursor = await db.execute("SELECT message_text FROM chat_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 100;", (top_user_id,))
        messages_rows = await cursor.fetchall()
        user_messages = [row[0] for row in messages_rows]
        return top_user_id, top_username, user_messages
async def _trim_history(db, user_id: int):
    await db.execute("DELETE FROM messages WHERE id IN ( SELECT id FROM messages WHERE user_id = ? AND role != 'system' ORDER BY id DESC LIMIT -1 OFFSET ? )", (user_id, MAX_HISTORY_LENGTH))
async def add_message_to_history(user_id: int, role: str, content: str):
    async with aiosqlite.connect(DB_PATH) as db: await db.execute( "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content) ); await _trim_history(db, user_id); await db.commit()
async def get_history(user_id: int) -> List[Dict[str, str]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT 1 FROM messages WHERE user_id = ? AND role = 'system' LIMIT 1", (user_id,)); system_prompt_exists = await cursor.fetchone()
        current_system_prompt = get_system_prompt()
        if not system_prompt_exists: await db.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, "system", current_system_prompt))
        else: await db.execute("UPDATE messages SET content = ? WHERE user_id = ? AND role = 'system'", (current_system_prompt, user_id))
        await db.commit(); cursor = await db.execute("SELECT role, content FROM messages WHERE user_id = ? ORDER BY id ASC", (user_id,)); rows = await cursor.fetchall()
        return [{"role": row[0], "content": row[1]} for row in rows]
async def clear_history(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db: await db.execute("DELETE FROM messages WHERE user_id = ?", (user_id,)); current_system_prompt = get_system_prompt(); await db.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, "system", current_system_prompt)); await db.commit()
    logger.info(f"История для пользователя {user_id} была очищена и сброшена на актуальную версию.")