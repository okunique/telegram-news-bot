# Telegram News Analysis Bot

Бот для сбора, анализа и перевода новостей из Telegram-каналов с возможностью генерации рыночных прогнозов.

---

## Полная инструкция по установке и запуску на чистом сервере (Linux/Ubuntu)

### 1. Установка системных зависимостей

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git postgresql postgresql-contrib libpq-dev
```

### 2. Создание пользователя и базы данных PostgreSQL

```bash
sudo -u postgres psql
```
В интерактивной консоли PostgreSQL:
```sql
CREATE USER newsbot_user WITH PASSWORD 'your_strong_password';
CREATE DATABASE newsbot OWNER newsbot_user;
\q
```

### 3. Клонирование репозитория

```bash
git clone https://github.com/okunique/telegram-news-bot.git
cd telegram-news-bot
```

### 4. Создание и активация виртуального окружения Python

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Установка Python-зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
touch .env
nano .env
```

Пример содержимого:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
SOURCE_CHANNEL_IDS=-1001234567890,-1009876543210
TARGET_CHANNEL_ID=-1001122334455
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=newsbot
POSTGRES_USER=newsbot_user
POSTGRES_PASSWORD=your_strong_password
```

- `SOURCE_CHANNEL_IDS` — ID исходных каналов через запятую (минус обязателен для публичных/приватных каналов)
- `TARGET_CHANNEL_ID` — ID вашего личного канала для публикации

### 7. Миграция базы данных (Alembic)

```bash
alembic upgrade head
```

Если alembic не найден, установите его:
```bash
pip install alembic
```

### 8. Запуск бота

```bash
python -m bot.main
```

---

## Рекомендации по безопасности
- Никогда не публикуйте свой `.env` и токены в открытом доступе
- Используйте сложные пароли для PostgreSQL
- Для production-сервера используйте отдельного пользователя Linux и ограничьте права доступа к файлам
- Рекомендуется запускать бота через supervisor/systemd для автозапуска и мониторинга

---

## Быстрый старт (TL;DR)
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git postgresql libpq-dev
sudo -u postgres psql -c "CREATE USER newsbot_user WITH PASSWORD 'your_strong_password';"
sudo -u postgres psql -c "CREATE DATABASE newsbot OWNER newsbot_user;"
git clone https://github.com/okunique/telegram-news-bot.git
cd telegram-news-bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # или создайте вручную
alembic upgrade head
python -m bot.main
```

---

## Пример systemd unit для автозапуска (опционально)

Создайте файл `/etc/systemd/system/newsbot.service`:

```
[Unit]
Description=Telegram News Analysis Bot
After=network.target postgresql.service

[Service]
User=your_linux_user
WorkingDirectory=/path/to/telegram-news-bot
Environment="PATH=/path/to/telegram-news-bot/venv/bin"
ExecStart=/path/to/telegram-news-bot/venv/bin/python -m bot.main
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable newsbot
sudo systemctl start newsbot
sudo systemctl status newsbot
```

---

## Команды бота

- `/start` — Начало работы с ботом
- `/status` — Проверка статуса бота и соединения
- `/digest 1h` — Дайджест за последний час
- `/digest 24h` — Дайджест за сутки

---

## Структура проекта

```
bot/
  ├── main.py           # Основной файл бота
  ├── handlers.py       # Обработчики команд
  ├── models.py         # Модели базы данных
  ├── config.py         # Конфигурация
  ├── openrouter_client.py  # Клиент OpenRouter API
  └── media_handler.py  # Обработчик медиафайлов
alembic/               # Миграции базы данных
.env                   # Конфигурация окружения
requirements.txt       # Зависимости
README.md              # Документация
```

---

## Лицензия

MIT 