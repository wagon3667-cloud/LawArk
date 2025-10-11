# 🚀 Инструкция по установке LawArk

## 📋 Предварительные требования

- Python 3.9 или выше
- Windows/Linux/macOS
- Telegram Bot Token
- Deepseek API ключ

## 🔧 Пошаговая установка

### 1. Установка Python зависимостей

```bash
# Перейдите в папку проекта
cd LawArk

# Установите зависимости
pip install -r requirements.txt
```

### 2. Установка Tesseract OCR

#### Windows:
1. Скачайте Tesseract с официального сайта: https://github.com/UB-Mannheim/tesseract/wiki
2. Установите в папку по умолчанию (обычно `C:\Program Files\Tesseract-OCR`)
3. Добавьте путь к tesseract.exe в переменную PATH

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-rus -y
```

#### macOS:
```bash
brew install tesseract tesseract-lang
```

### 3. Настройка окружения

1. Откройте файл `.env`
2. Замените значения на реальные:

```env
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
DATABASE_PATH=lawark.db
MAX_FILE_SIZE_MB=20
```

### 4. Получение токенов

#### Telegram Bot Token:
1. Напишите @BotFather в Telegram
2. Выполните команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

#### Deepseek API ключ:
1. Зарегистрируйтесь на https://platform.deepseek.com/
2. Перейдите в раздел API Keys
3. Создайте новый ключ
4. Скопируйте ключ

## 🧪 Тестирование

Запустите тест для проверки работоспособности:

```bash
python test_bot.py
```

Если все тесты пройдены успешно, можно запускать бота.

## 🚀 Запуск бота

```bash
python main.py
```

При успешном запуске вы увидите:
```
INFO - База данных инициализирована
INFO - Бот LawArk запущен
```

## 🔧 Решение проблем

### Ошибка "BOT_TOKEN не найден"
- Проверьте файл `.env`
- Убедитесь, что токен скопирован полностью

### Ошибка Tesseract
- Убедитесь, что Tesseract установлен
- Проверьте переменную PATH
- На Windows: добавьте путь к tesseract.exe

### Ошибка импорта модулей
- Установите все зависимости: `pip install -r requirements.txt`
- Проверьте версию Python (должна быть 3.9+)

### Ошибка Deepseek API
- Проверьте правильность API ключа
- Убедитесь, что у вас есть доступ к API

## 📊 Мониторинг

Логи сохраняются в файл `lawark.log` и выводятся в консоль.

Для просмотра логов в реальном времени:
```bash
tail -f lawark.log
```

## 🔄 Обновление

1. Остановите бота (Ctrl+C)
2. Обновите код
3. Установите новые зависимости (если есть)
4. Запустите заново

## 🛠 Разработка

Для разработки рекомендуется использовать виртуальное окружение:

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/macOS)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в файле `lawark.log`
2. Убедитесь, что все зависимости установлены
3. Проверьте правильность токенов в `.env`
4. Запустите тест: `python test_bot.py`
