from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_menu():
    """Главное меню бота"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="💬 Задать вопрос"))
    builder.add(KeyboardButton(text="📄 Анализ документа"))
    builder.add(KeyboardButton(text="💳 Подписка"))
    builder.add(KeyboardButton(text="📊 Статистика"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_subscription_menu():
    """Меню подписок"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🎁 Пробный период (7 дней)", callback_data="sub_trial"))
    builder.add(InlineKeyboardButton(text="📦 Базовый (499₽/мес)", callback_data="sub_basic"))
    builder.add(InlineKeyboardButton(text="🚀 Безлимит (999₽/мес)", callback_data="sub_unlimited"))
    builder.add(InlineKeyboardButton(text="🏢 Стартап (1499₽/мес)", callback_data="sub_startup"))
    builder.add(InlineKeyboardButton(text="👥 Команда (2999₽/мес)", callback_data="sub_team"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    builder.adjust(1)
    return builder.as_markup()

def get_payment_menu(plan_type: str, price: int):
    """Меню оплаты через Telegram Stars"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=f"💎 Оплатить {price} Stars",
        callback_data=f"pay_{plan_type}"
    ))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_subscription"))
    builder.adjust(1)
    return builder.as_markup()

def get_back_menu():
    """Кнопка назад"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    return builder.as_markup()

def get_healthark_promo():
    """Кнопка для перехода к HealthArk"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔗 Перейти к HealthArk", url="https://t.me/HealthArk_bot"))
    return builder.as_markup()

def get_consultation_type_menu():
    """Меню выбора типа консультации"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📝 Текстовый вопрос"))
    builder.add(KeyboardButton(text="📄 Загрузить документ"))
    builder.add(KeyboardButton(text="🔙 Главное меню"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
