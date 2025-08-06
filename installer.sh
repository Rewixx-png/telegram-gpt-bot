#!/bin/bash

# Скрипт автоматической установки и настройки Telegram GPT-бота
# Останавливаем выполнение при любой ошибке для безопасности
set -e

# --- Цвета для красивого вывода ---
C_RESET='\033[0m'
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_BLUE='\033[0;34m'
C_YELLOW='\033[0;33m'

# --- Глобальные переменные ---
REPO_URL="https"
PROJECT_DIR="" # Определим после клонирования

# --- Функции ---

# Функция для вывода красивого заголовка
print_header() {
    clear
    echo -e "${C_BLUE}
████████╗██████╗ ████████╗     ██████╗  ██████╗ ████████╗
╚══██╔══╝██╔══██╗╚══██╔══╝    ██╔═══██╗██╔═══██╗╚══██╔══╝
   ██║   ██████╔╝   ██║       ██║   ██║██║   ██║   ██║   
   ██║   ██╔══██╗   ██║       ██║   ██║██║   ██║   ██║   
   ██║   ██║  ██║   ██║       ╚██████╔╝╚██████╔╝   ██║   
   ╚═╝   ╚═╝  ╚═╝   ╚═╝        ╚═════╝  ╚═════╝    ╚═╝   
${C_RESET}"
    echo -e "${C_GREEN}Добро пожаловать в установщик Telegram GPT-бота!${C_RESET}"
    echo "----------------------------------------------------"
    echo "Этот скрипт автоматически установит и настроит все необходимое."
    echo ""
}

# Функция для проверки и установки зависимостей
check_dependencies() {
    echo -e "${C_YELLOW}Проверка системных зависимостей...${C_RESET}"
    for cmd in git python3 python3-pip; do
        if ! command -v $cmd &> /dev/null; then
            echo "Команда '$cmd' не найдена. Установка..."
            sudo apt-get update
            sudo apt-get install -y $cmd
        else
            echo -e "✅ $cmd - ${C_GREEN}найден.${C_RESET}"
        fi
    done
    echo ""
}

# Функция для клонирования репозитория
clone_repo() {
    read -p "Введите HTTPS URL вашего репозитория на GitHub: " REPO_URL
    PROJECT_DIR=$(basename "$REPO_URL" .git)
    
    if [ -d "$PROJECT_DIR" ]; then
        echo -e "${C_YELLOW}Директория '$PROJECT_DIR' уже существует. Пропускаем клонирование.${C_RESET}"
    else
        echo "Клонирование проекта из $REPO_URL..."
        git clone "$REPO_URL"
        echo -e "${C_GREEN}Проект успешно склонирован в папку '$PROJECT_DIR'.${C_RESET}"
    fi
    cd "$PROJECT_DIR"
    echo ""
}

# Функция для сбора данных конфигурации у пользователя
gather_config_data() {
    echo "----------------------------------------------------"
    echo -e "${C_GREEN}Теперь давайте настроим вашего бота.${C_RESET}"
    echo "Пожалуйста, введите следующие данные:"
    echo ""

    read -p "1. Введите токен вашего Telegram-бота (от @BotFather): " TELEGRAM_TOKEN
    read -p "2. Введите ваш личный Telegram ID (от @userinfobot): " ADMIN_ID
    read -p "3. Введите ID группового чата (должен быть отрицательным): " ALLOWED_CHAT_ID
    read -p "4. Введите ваш API ключ от OpenAI/ChatAnywhere: " OPENAI_API_KEY
    echo ""
}

# Функция для создания файла config.py
create_config_file() {
    echo -e "${C_YELLOW}Создание конфигурационного файла config.py...${C_RESET}"
    
    # Используем cat с HERE-документом для безопасного создания файла
    cat << EOF > config_data/config.py
# Этот файл был сгенерирован автоматически скриптом installer.sh

from dataclasses import dataclass

@dataclass
class BotConfig:
    token: str
    admin_id: int

@dataclass
class GptConfig:
    api_key: str
    base_url: str
    model: str

@dataclass
class Settings:
    allowed_chat_id: int

@dataclass
class Config:
    bot: BotConfig
    gpt: GptConfig
    settings: Settings

def load_config():
    return Config(
        bot=BotConfig(
            token='$TELEGRAM_TOKEN',
            admin_id=$ADMIN_ID
        ),
        gpt=GptConfig(
            api_key="$OPENAI_API_KEY",
            base_url="https://api.chatanywhere.tech/v1",
            model="gpt-4o-mini"
        ),
        settings=Settings(
            allowed_chat_id=$ALLOWED_CHAT_ID
        )
    )

config = load_config()
EOF

    echo -e "${C_GREEN}✅ Файл config.py успешно создан!${C_RESET}"
    echo ""
}

# Функция для установки Python-зависимостей
setup_python_env() {
    echo -e "${C_YELLOW}Установка Python-зависимостей из requirements.txt...${C_RESET}"
    pip3 install -r requirements.txt
    echo -e "${C_GREEN}✅ Зависимости успешно установлены!${C_RESET}"
    echo ""
}

# Основная функция-оркестратор
main() {
    print_header
    check_dependencies
    clone_repo
    gather_config_data
    create_config_file
    setup_python_env

    echo "----------------------------------------------------"
    echo -e "${C_GREEN}🎉 Установка завершена! 🎉${C_RESET}"
    echo "Вы находитесь в директории проекта: $(pwd)"
    echo ""
    echo -e "${C_YELLOW}Чтобы запустить бота, выполните команду:${C_RESET}"
    echo -e "  ${C_BLUE}python3 bot.py${C_RESET}"
    echo ""
    echo "Для запуска в фоновом режиме используйте 'screen'."
    echo ""
}

# --- Запуск скрипта ---
main