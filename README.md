# ⚖️ LawArk - AI Юридический Бот

Telegram бот для юридических консультаций с анализом документов на основе AI.

## 🚀 Возможности

- 💬 Юридические консультации с AI
- 📄 Анализ документов (PDF, DOCX, изображения)
- 🔍 OCR распознавание текста
- 💳 Система подписок
- 📊 Статистика использования
- 🔗 Кросс-промо с HealthArk

## 📋 Требования

- Python 3.9+
- Tesseract OCR
- Deepseek API ключ
- Telegram Bot Token

## 🔧 Установка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd LawArk
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Установка Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-rus -y
```

**Windows:**
Скачайте с официального сайта: https://github.com/UB-Mannheim/tesseract/wiki

**macOS:**
```bash
brew install tesseract tesseract-lang
```

### 4. Настройка окружения
Создайте файл `.env` и заполните его:
```env
BOT_TOKEN=your_bot_token_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DATABASE_PATH=lawark.db
MAX_FILE_SIZE_MB=20
```

## 🚀 Запуск

```bash
python main.py
```

## 📁 Структура проекта

```
LawArk/
├── main.py                 # Главный файл
├── .env                   # Переменные окружения
├── requirements.txt       # Зависимости
├── README.md             # Документация
├── lawark.log           # Лог файл
└── src/
    ├── handlers/         # Обработчики сообщений
    │   ├── start.py
    │   ├── consultation.py
    │   ├── documents.py
    │   └── payment.py
    ├── services/         # Сервисы
    │   ├── ai_service.py
    │   ├── ocr_service.py
    │   └── subscription_service.py
    ├── database/         # База данных
    │   └── database.py
    └── utils/           # Утилиты
        ├── config.py
        ├── keyboards.py
        └── prompts.py
```

## 💰 Тарифные планы

### Физические лица
- **Пробный**: 7 дней бесплатно (5 консультаций)
- **Базовый**: 499₽/мес (20 консультаций)
- **Безлимит**: 999₽/мес

### Бизнес
- **Стартап**: 1499₽/мес (безлимит)
- **Команда**: 2999₽/мес (5 пользователей)

## 📄 Поддерживаемые форматы

- **Изображения**: JPG, PNG
- **Документы**: PDF, DOCX
- **Максимальный размер**: 20MB

## 🔧 API интеграции

- **Deepseek API**: для AI консультаций
- **Tesseract OCR**: для распознавания текста
- **Telegram Bot API**: для взаимодействия

## 📊 База данных

SQLite база данных с таблицами:
- `users` - пользователи и подписки
- `consultations` - история консультаций
- `subscriptions` - история платежей

## 🛠 Разработка

### Запуск в режиме разработки
```bash
# Установка в виртуальном окружении
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python main.py
```

### Логирование
Логи сохраняются в файл `lawark.log` и выводятся в консоль.

## 📝 Лицензия

MIT License

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи в файле `lawark.log`
2. Убедитесь, что все зависимости установлены
3. Проверьте правильность токенов в `.env`
