<h1 align="center">🤖 Telegram GPT Bot 🤖</h1>

<p align="center">
  Ваш персональный ИИ-ассистент и помощник в группах, работающий на `aiogram 3.x` и API OpenAI.
</p>

<p align="center">
  <!-- GitHub Badges -->
  <a href="https://github.com/Rewixx-png/telegram-gpt-bot/stargazers"><img src="https://img.shields.io/github/stars/Rewixx-png/telegram-gpt-bot?style=for-the-badge&logo=github&color=gold" alt="Stars"></a>
  <a href="https://github.com/Rewixx-png/telegram-gpt-bot/network/members"><img src="https://img.shields.io/github/forks/Rewixx-png/telegram-gpt-bot?style=for-the-badge&logo=github&color=blue" alt="Forks"></a>
  <img src="https://img.shields.io/github/last-commit/Rewixx-png/telegram-gpt-bot?style=for-the-badge&logo=github&color=informational" alt="Last Commit">
  <img src="https://img.shields.io/github/repo-size/Rewixx-png/telegram-gpt-bot?style=for-the-badge&logo=github" alt="Repo Size">
  <!-- Python & Aiogram Badges -->
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version"></a>
  <a href="https://aiogram.dev/"><img src="https://img.shields.io/badge/Aiogram-3.x-green?style=for-the-badge&logo=telegram" alt="Aiogram Version"></a>
</p>

---

Проект многофункционального Telegram-бота с чистой, модульной архитектурой для легкого расширения и поддержки.

### ✨ Ключевые фичи

*   ✅ **Автоматический установщик:** Интерактивный скрипт `installer.sh` для быстрой и удобной настройки "под ключ".
*   🧠 **Работа в группах:** Бот отвечает на сообщения пользователей прямо в "Темах" (топиках) группового чата.
*   🔒 **Приватность и контроль:** Работает только в одном, заранее заданном чате, и как личный ассистент для владельца.
*   🤖 **Модульная структура:** Код разделен на логические блоки для легкого расширения функционала.
*   🚀 **Высокая производительность:** Полностью асинхронный код на `aiogram 3.x` не блокируется во время ожидания ответа от ИИ.

---

## 🚀 Быстрый старт (Рекомендуемый способ)

Для максимального удобства используйте автоматический установщик. Он сделает всю грязную работу за вас.

> 💡 **Подсказка:** Просто скопируйте и выполните эти три команды на вашем сервере (например, Ubuntu/Debian).

1.  **Скачайте установщик:**
    ```bash
    wget https://raw.githubusercontent.com/Rewixx-png/telegram-gpt-bot/main/installer.sh
    ```

2.  **Дайте права на выполнение:**
    ```bash
    chmod +x installer.sh
    ```

3.  **Запустите скрипт и следуйте инструкциям на экране:**
    ```bash
    ./installer.sh
    ```
Скрипт задаст вам все необходимые вопросы и автоматически настроит проект. После завершения его работы вы окажетесь в папке с ботом, готовым к запуску.

---

## ✅ Обязательные шаги после установки

Эти действия нужно выполнить независимо от выбранного способа установки.

### 1. Настройка бота в Telegram

*   **Отключите режим приватности:**
    *   Найдите в Telegram **@BotFather**.
    *   Выполните `/mybots` -> выберите вашего бота.
    *   `Bot Settings` -> `Group Privacy` -> `Turn off`.
    *   *Это позволит боту видеть все сообщения в группе, а не только команды.*

*   **Добавьте бота в группу:**
    *   Добавьте вашего бота в нужный групповой чат.
    *   Назначьте его администратором с правом на отправку сообщений.

### 2. Запуск бота

Для простого запуска выполните команду в папке проекта:
```bash
python3 bot.py
```
Для того чтобы бот работал 24/7 в фоновом режиме, используйте `screen`:

```bash
# Запустить новую сессию с именем gpt-bot
screen -S gpt-bot

# Внутри сессии запустить бота
python3 bot.py

# Выйти из сессии, оставив ее работать (нажмите Ctrl+A, затем D)
```

> Чтобы вернуться в сессию и посмотреть логи, используйте команду `screen -r gpt-bot`.

---

<details>
<summary>🛠️ <b>Ручная установка (для опытных пользователей)</b></summary>

<br>

Если вы предпочитаете настраивать все вручную, следуйте этим шагам.

#### 1. Клонирование репозитория
```bash
git clone https://github.com/Rewixx-png/telegram-gpt-bot.git
cd telegram-gpt-bot
```

#### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 3. Настройка конфигурации
Конфигурационный файл с токенами не хранится в репозитории из соображений безопасности.

1.  Скопируйте файл-шаблон `config.py.example` в новый файл `config.py`:
    ```bash
    cp config_data/config.py.example config_data/config.py
    ```

2.  Откройте **новый** файл `config_data/config.py` и укажите в нем ваши данные:
    *   `token`: Токен вашего Telegram-бота.
    *   `admin_id`: Ваш личный Telegram ID.
    *   `api_key`: Ваш ключ от OpenAI.
    *   `allowed_chat_id`: ID группового чата.

После этого переходите к [общим шагам после установки](#-общие-шаги-после-установки).

</details>

<details>
<summary>📂 <b>Структура проекта</b></summary>

<br>

```
/
|-- bot.py                          # 🚀 Главный файл для запуска бота
|-- installer.sh                    # 🪄 Автоматический установщик
|-- requirements.txt                # 📦 Список зависимостей проекта
|-- .gitignore                      # 🛡️ Файл, скрывающий секретные данные от Git
|-- README.md                       # 📄 Эта документация
|
|-- config_data/
|   |-- config.py.example           # ⚙️ Шаблон файла для хранения токенов и настроек
|
|-- handlers/
|   |-- topic_handler.py             # 🧠 Логика обработки сообщений в групповых топиках
|   |-- private_chat_handler.py      # 👤 Логика обработки личных сообщений от админа
|
|-- services/
|   |-- gpt_service.py              # 🤖 Модуль для общения с API OpenAI
```

</details>

## 📜 Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле `LICENSE`.