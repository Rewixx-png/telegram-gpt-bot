# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Playwright и его зависимости (браузер) для скриншотов.
# ВНИМАНИЕ: Это, блядь, добавит веса нашему образу.
# <-- ВОТ ЭТА СТРОКА ТЕПЕРЬ ПРАВИЛЬНАЯ
RUN python -m playwright install --with-deps chromium

# Копируем весь остальной код проекта в рабочую директорию
COPY . .

# Указываем команду для запуска бота при старте контейнера
CMD ["python3", "bot.py"]