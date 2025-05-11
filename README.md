# Telegram News Analysis Bot

Бот для автоматизации работы с новостями в Telegram, включающий классификацию, перевод и прогнозирование рынка.

## Возможности

- Автоматический мониторинг новостных каналов
- Классификация новостей по категориям
- Перевод новостей на русский язык
- Анализ влияния на рынок
- Автоматическая публикация в целевой канал

## Быстрая установка

Для быстрой установки на чистый сервер выполните:

```bash
# Скачайте скрипт установки
curl -O https://raw.githubusercontent.com/okunique/telegram-news-bot/master/install.sh

# Сделайте скрипт исполняемым
chmod +x install.sh

# Запустите установку
sudo ./install.sh
```

После установки:
1. Отредактируйте файл `.env` и укажите ваши токены
2. Проверьте статус сервиса: `systemctl status newsbot`
3. Посмотрите логи: `journalctl -u newsbot -f`

## Ручная установка

Если вы хотите установить бота вручную, следуйте этим шагам:

### 1. Системные зависимости

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-venv python3-pip git postgresql postgresql-contrib libpq-dev
```

### 2. Настройка PostgreSQL

```bash
# Создание пользователя и базы данных
sudo -u postgres psql -c "CREATE USER newsbot_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE newsbot OWNER newsbot_user;"
```

### 3. Клонирование репозитория

```bash
git clone https://github.com/okunique/telegram-news-bot.git
cd telegram-news-bot
```

### 4. Настройка Python окружения

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Конфигурация

Создайте файл `.env` в корневой директории проекта:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
SOURCE_CHANNEL_IDS=-1001234567890,-1009876543210
TARGET_CHANNEL_ID=-1001122334455
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=newsbot
POSTGRES_USER=newsbot_user
POSTGRES_PASSWORD=your_password
```

### 6. Миграция базы данных

```bash
alembic upgrade head
```

### 7. Запуск бота

```bash
# Запуск в режиме разработки
python -m bot.main

# Или через systemd (рекомендуется для продакшена)
sudo cp newsbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable newsbot
sudo systemctl start newsbot
```

## Структура проекта

```
telegram-news-bot/
├── alembic/              # Миграции базы данных
├── bot/
│   ├── __init__.py
│   ├── main.py          # Точка входа
│   ├── config.py        # Конфигурация
│   ├── database.py      # Работа с БД
│   ├── handlers/        # Обработчики команд
│   ├── services/        # Бизнес-логика
│   └── utils/           # Вспомогательные функции
├── tests/               # Тесты
├── .env                 # Конфигурация (не в репозитории)
├── .gitignore
├── alembic.ini
├── install.sh          # Скрипт автоматической установки
├── requirements.txt
└── README.md
```

## Требования

- Python 3.8+
- PostgreSQL 12+
- Telegram Bot Token
- OpenRouter API Key

## Безопасность

- Храните токены и пароли в `.env` файле
- Не публикуйте `.env` файл в репозиторий
- Используйте отдельного пользователя для базы данных
- Регулярно обновляйте зависимости
- Настройте брандмауэр
- Используйте HTTPS для API запросов

## Поддержка

При возникновении проблем:
1. Проверьте логи: `journalctl -u newsbot -f`
2. Убедитесь, что все токены указаны правильно
3. Проверьте доступность API сервисов
4. Создайте issue в репозитории

## Лицензия

MIT 