from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..utils.keyboards import get_main_menu, get_subscription_menu
from ..utils.prompts import HEALTHARK_PROMO
from ..database.database import Database
from ..services.subscription_service import SubscriptionService

router = Router()

class MainStates(StatesGroup):
    main_menu = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    db = Database()
    await db.init_db()
    
    # Создаем или получаем пользователя
    user = await db.get_or_create_user(
        message.from_user.id, 
        message.from_user.username
    )
    
    welcome_text = """⚖️ Добро пожаловать в LawArk!

Ваш AI-юрист 24/7

Я помогу с:
✓ Юридическими консультациями
✓ Анализом документов
✓ Разъяснением законов РФ

🎁 7 дней бесплатно!

Выберите действие:"""
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu()
    )
    await state.set_state(MainStates.main_menu)

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """📖 Справка по LawArk

🔹 /start - Главное меню
🔹 /help - Эта справка
🔹 /subscription - Управление подпиской

💬 Консультации:
• Задавайте юридические вопросы
• Загружайте документы для анализа
• Получайте развернутые ответы

📄 Поддерживаемые форматы:
• Изображения: JPG, PNG
• Документы: PDF, DOCX

💰 Тарифы:
• Пробный: 7 дней бесплатно
• Базовый: 499₽/мес (20 консультаций)
• Безлимит: 999₽/мес
• Бизнес планы от 1499₽/мес"""
    
    await message.answer(help_text)

@router.message(Command("subscription"))
async def cmd_subscription(message: Message):
    """Обработчик команды /subscription"""
    db = Database()
    subscription_service = SubscriptionService(db)
    
    summary = await subscription_service.get_user_subscription_summary(message.from_user.id)
    
    await message.answer(
        f"{summary}\n\nВыберите новый план:",
        reply_markup=get_subscription_menu()
    )

@router.message(F.text == "💳 Подписка")
async def subscription_menu(message: Message):
    """Обработчик кнопки подписки"""
    db = Database()
    subscription_service = SubscriptionService(db)
    
    summary = await subscription_service.get_user_subscription_summary(message.from_user.id)
    
    await message.answer(
        f"{summary}\n\nВыберите новый план:",
        reply_markup=get_subscription_menu()
    )

@router.message(F.text == "📊 Статистика")
async def user_stats(message: Message):
    """Показать статистику пользователя"""
    db = Database()
    stats = await db.get_user_stats(message.from_user.id)
    
    stats_text = f"""📊 Ваша статистика:

📈 Консультаций: {stats['consultations_count']}
📦 План: {stats['plan_info'].get('name', 'Неизвестно')}
✅ Статус: {'Активна' if stats['subscription']['is_active'] else 'Неактивна'}

💡 Совет: Используйте регулярные консультации для решения правовых вопросов."""
    
    await message.answer(stats_text)

@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню"""
    await callback.message.edit_text(
        "⚖️ LawArk - Ваш AI-юрист 24/7\n\nВыберите действие:",
        reply_markup=get_main_menu()
    )
    await state.set_state(MainStates.main_menu)
    await callback.answer()

# Обработчик для показа кросс-промо с HealthArk
@router.message(F.text.contains("✅ Вопрос решен!"))
async def show_healthark_promo(message: Message):
    """Показать промо HealthArk после решения вопроса"""
    from ..utils.keyboards import get_healthark_promo
    
    await message.answer(
        HEALTHARK_PROMO,
        reply_markup=get_healthark_promo()
    )
