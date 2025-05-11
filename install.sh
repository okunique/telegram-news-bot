#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Функция для вывода сообщений
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверка на root права
if [ "$EUID" -ne 0 ]; then 
    print_error "Этот скрипт должен быть запущен с правами root (sudo)"
    exit 1
fi

# Проверка наличия необходимых утилит
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 не установлен. Устанавливаем..."
        return 1
    fi
    return 0
}

# Установка системных зависимостей
print_message "Обновление списка пакетов..."
apt update && apt upgrade -y

print_message "Установка системных зависимостей..."
apt install -y python3 python3-venv python3-pip git postgresql postgresql-contrib libpq-dev

# Настройка PostgreSQL
print_message "Настройка PostgreSQL..."
DB_USER="newsbot_user"
DB_NAME="newsbot"
DB_PASS=$(openssl rand -base64 12)

sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Клонирование репозитория
print_message "Клонирование репозитория..."
if [ -d "telegram-news-bot" ]; then
    print_warning "Директория telegram-news-bot уже существует. Обновляем..."
    cd telegram-news-bot
    git pull
else
    git clone https://github.com/okunique/telegram-news-bot.git
    cd telegram-news-bot
fi

# Создание и активация виртуального окружения
print_message "Создание виртуального окружения Python..."
python3 -m venv venv
source venv/bin/activate

# Установка Python-зависимостей
print_message "Установка Python-зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание .env файла
print_message "Создание конфигурационного файла..."
cat > .env << EOL
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
SOURCE_CHANNEL_IDS=-1001234567890,-1009876543210
TARGET_CHANNEL_ID=-1001122334455
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASS
EOL

print_message "Пароль для базы данных: $DB_PASS"
print_warning "Не забудьте отредактировать .env файл и указать правильные токены!"

# Миграция базы данных
print_message "Применение миграций базы данных..."
alembic upgrade head

# Создание systemd сервиса
print_message "Создание systemd сервиса..."
cat > /etc/systemd/system/newsbot.service << EOL
[Unit]
Description=Telegram News Analysis Bot
After=network.target postgresql.service

[Service]
User=$SUDO_USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=$(pwd)/venv/bin/python -m bot.main
Restart=always
RestartSec=10
StandardOutput=append:/var/log/newsbot.log
StandardError=append:/var/log/newsbot.error.log

[Install]
WantedBy=multi-user.target
EOL

# Создание лог-файлов
touch /var/log/newsbot.log /var/log/newsbot.error.log
chown $SUDO_USER:$SUDO_USER /var/log/newsbot.log /var/log/newsbot.error.log
chmod 644 /var/log/newsbot.log /var/log/newsbot.error.log

# Перезагрузка systemd и запуск сервиса
print_message "Запуск сервиса..."
systemctl daemon-reload
systemctl enable newsbot
systemctl start newsbot

# Проверка статуса
print_message "Проверка статуса сервиса..."
systemctl status newsbot

print_message "Установка завершена!"
print_message "Не забудьте отредактировать .env файл и указать правильные токены!"
print_message "Логи сервиса можно посмотреть командой: journalctl -u newsbot -f" 