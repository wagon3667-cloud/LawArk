from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from ..utils.keyboards import get_subscription_menu, get_payment_menu, get_main_menu
from ..database.database import Database
from ..services.subscription_service import SubscriptionService
from ..utils.config import SUBSCRIPTION_PLANS

router = Router()

@router.callback_query(F.data.startswith("sub_"))
async def handle_subscription_selection(callback: CallbackQuery):
    """Обработать выбор подписки"""
    plan_type = callback.data.replace("sub_", "")
    
    if plan_type not in SUBSCRIPTION_PLANS:
        await callback.answer("❌ Неверный тип подписки", show_alert=True)
        return
    
    db = Database()
    subscription_service = SubscriptionService(db)
    
    # Проверяем, может ли пользователь подписаться
    can_subscribe = await subscription_service.can_user_subscribe(
        callback.from_user.id, 
        plan_type
    )
    
    if not can_subscribe['can_subscribe']:
        await callback.answer(can_subscribe['message'], show_alert=True)
        return
    
    plan_info = SUBSCRIPTION_PLANS[plan_type]
    
    # Показываем информацию о плане
    plan_description = f"""📦 {plan_info['name']}

💰 Цена: {plan_info['price']}₽
⏱ Срок: {plan_info['duration_days']} дней"""

    if plan_info['consultations_limit'] == -1:
        plan_description += "\n📊 Консультации: безлимит"
    else:
        plan_description += f"\n📊 Консультации: {plan_info['consultations_limit']}/мес"
    
    if plan_type == 'trial':
        plan_description += "\n\n🎁 Пробный период - абсолютно бесплатно!"
    
    await callback.message.edit_text(
        plan_description,
        reply_markup=get_payment_menu(plan_type, plan_info['price'])
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pay_"))
async def handle_payment(callback: CallbackQuery):
    """Обработать оплату"""
    plan_type = callback.data.replace("pay_", "")
    
    if plan_type not in SUBSCRIPTION_PLANS:
        await callback.answer("❌ Неверный тип подписки", show_alert=True)
        return
    
    db = Database()
    subscription_service = SubscriptionService(db)
    
    # Проверяем, может ли пользователь подписаться
    can_subscribe = await subscription_service.can_user_subscribe(
        callback.from_user.id, 
        plan_type
    )
    
    if not can_subscribe['can_subscribe']:
        await callback.answer(can_subscribe['message'], show_alert=True)
        return
    
    plan_info = SUBSCRIPTION_PLANS[plan_type]
    
    if plan_type == 'trial':
        # Активируем пробный период без оплаты
        result = await subscription_service.activate_subscription(
            callback.from_user.id,
            plan_type
        )
        
        if result['success']:
            await callback.message.edit_text(
                f"✅ {result['message']}!\n\n"
                "🎉 Добро пожаловать в LawArk!\n"
                "Теперь вы можете задавать вопросы и анализировать документы.",
                reply_markup=get_main_menu()
            )
        else:
            await callback.message.edit_text(
                f"❌ {result['message']}",
                reply_markup=get_subscription_menu()
            )
    else:
        # Для платных подписок показываем информацию об оплате
        payment_info = f"""💳 Оплата подписки "{plan_info['name']}"

💰 Сумма: {plan_info['price']}₽
💎 В Telegram Stars: {plan_info['price']} Stars

📝 Инструкция по оплате:
1. Нажмите кнопку ниже
2. Подтвердите оплату в Telegram
3. Подписка активируется автоматически

⚠️ Оплата производится через Telegram Stars"""
        
        # Здесь можно интегрировать с Telegram Payments API
        # Пока просто симулируем успешную оплату
        await callback.message.edit_text(
            payment_info,
            reply_markup=get_subscription_menu()
        )
        
        # Симуляция успешной оплаты (в реальном проекте здесь будет обработка webhook)
        await simulate_payment_success(callback.from_user.id, plan_type)
    
    await callback.answer()

async def simulate_payment_success(user_id: int, plan_type: str):
    """Симуляция успешной оплаты (для демо)"""
    # В реальном проекте это будет webhook от Telegram Payments
    db = Database()
    subscription_service = SubscriptionService(db)
    
    result = await subscription_service.activate_subscription(user_id, plan_type)
    
    if result['success']:
        # Отправляем уведомление об успешной активации
        # В реальном проекте это можно сделать через отдельный сервис уведомлений
        pass

@router.callback_query(F.data == "back_subscription")
async def back_to_subscription(callback: CallbackQuery):
    """Вернуться к выбору подписки"""
    await callback.message.edit_text(
        "💳 Выберите подписку:",
        reply_markup=get_subscription_menu()
    )
    await callback.answer()

# Обработчик для успешных платежей (webhook)
@router.message(F.successful_payment)
async def handle_successful_payment(message: Message):
    """Обработать успешный платеж"""
    # В реальном проекте здесь будет обработка успешного платежа
    # и активация соответствующей подписки
    await message.answer(
        "✅ Платеж успешно обработан!\n"
        "Подписка активирована.",
        reply_markup=get_main_menu()
    )
