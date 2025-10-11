import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", "lawark.db")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 20))

# Subscription plans
SUBSCRIPTION_PLANS = {
    "trial": {
        "name": "Пробный период",
        "duration_days": 7,
        "price": 0,
        "consultations_limit": 5
    },
    "basic": {
        "name": "Базовый",
        "duration_days": 30,
        "price": 499,
        "consultations_limit": 20
    },
    "unlimited": {
        "name": "Безлимит",
        "duration_days": 30,
        "price": 999,
        "consultations_limit": -1
    },
    "startup": {
        "name": "Стартап",
        "duration_days": 30,
        "price": 1499,
        "consultations_limit": -1
    },
    "team": {
        "name": "Команда",
        "duration_days": 30,
        "price": 2999,
        "consultations_limit": -1
    }
}

# Supported file types
SUPPORTED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png']
SUPPORTED_DOCUMENT_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
