# Telegram News Analysis Bot

Бот для сбора, анализа и перевода новостей из Telegram-каналов с возможностью генерации рыночных прогнозов.

## Возможности

- Автоматический сбор новостей из указанных Telegram-каналов
- Перевод новостей на русский язык
- Анализ тематики и важности новостей
- Классификация по рыночным направлениям (TradFi/Crypto)
- Генерация аналитических дайджестов
- Построение рыночных прогнозов

## Требования

- Python 3.8+
- PostgreSQL 12+
- Telegram Bot Token
- OpenRouter API Key

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd telegram-news-bot
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
pip install -r requirements.txt
```

3. Создайте файл .env и заполните его:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_api_key
SOURCE_CHANNEL_IDS=channel1,channel2
TARGET_CHANNEL_ID=your_channel
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=newsbot
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
```

4. Инициализируйте базу данных:
```bash
alembic upgrade head
```

## Запуск

```bash
python -m bot.main
```

## Команды бота

- `/start` - Начало работы с ботом
- `/status` - Проверка статуса бота
- `/digest 1h` - Получить дайджест за последний час
- `/digest 24h` - Получить дайджест за последние сутки

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
README.md             # Документация
```

## Лицензия

MIT 