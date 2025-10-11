from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..utils.config import SUBSCRIPTION_PLANS
from ..database.database import Database

class SubscriptionService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_plan_info(self, plan_type: str) -> Dict[str, Any]:
        """Получить информацию о тарифном плане"""
        return SUBSCRIPTION_PLANS.get(plan_type, {})
    
    def get_all_plans(self) -> Dict[str, Dict[str, Any]]:
        """Получить все доступные планы"""
        return SUBSCRIPTION_PLANS
    
    async def can_user_subscribe(self, user_id: int, plan_type: str) -> Dict[str, Any]:
        """Проверить, может ли пользователь подписаться на план"""
        if plan_type not in SUBSCRIPTION_PLANS:
            return {
                'can_subscribe': False,
                'reason': 'invalid_plan',
                'message': 'Неверный тип подписки'
            }
        
        # Получаем информацию о пользователе
        user = await self.db.get_or_create_user(user_id)
        subscription_status = await self.db.get_user_subscription_status(user_id)
        
        # Проверяем, активна ли уже подписка
        if subscription_status['is_active']:
            return {
                'can_subscribe': False,
                'reason': 'active_subscription',
                'message': 'У вас уже есть активная подписка'
            }
        
        # Проверяем пробный период
        if plan_type == 'trial' and user['trial_used']:
            return {
                'can_subscribe': False,
                'reason': 'trial_used',
                'message': 'Пробный период уже использован'
            }
        
        return {
            'can_subscribe': True,
            'plan_info': SUBSCRIPTION_PLANS[plan_type]
        }
    
    async def activate_subscription(self, user_id: int, plan_type: str) -> Dict[str, Any]:
        """Активировать подписку"""
        if plan_type not in SUBSCRIPTION_PLANS:
            return {
                'success': False,
                'message': 'Неверный тип подписки'
            }
        
        plan_info = SUBSCRIPTION_PLANS[plan_type]
        
        # Обновляем подписку в базе данных
        await self.db.update_user_subscription(
            user_id, 
            plan_type, 
            plan_info['duration_days']
        )
        
        # Если это пробный период, отмечаем его как использованный
        if plan_type == 'trial':
            await self.db.mark_trial_used(user_id)
        
        # Добавляем запись об оплате (если это не пробный период)
        if plan_info['price'] > 0:
            await self.db.add_subscription_payment(
                user_id, 
                plan_type, 
                plan_info['price']
            )
        
        return {
            'success': True,
            'message': f'Подписка "{plan_info["name"]}" активирована',
            'plan_info': plan_info
        }
    
    def format_subscription_info(self, plan_type: str) -> str:
        """Форматировать информацию о подписке"""
        plan = SUBSCRIPTION_PLANS.get(plan_type, {})
        if not plan:
            return "Неизвестный план"
        
        info = f"📦 {plan['name']}\n"
        info += f"💰 Цена: {plan['price']}₽\n"
        info += f"⏱ Срок: {plan['duration_days']} дней\n"
        
        if plan['consultations_limit'] == -1:
            info += "📊 Консультации: безлимит\n"
        else:
            info += f"📊 Консультации: {plan['consultations_limit']}/мес\n"
        
        return info
    
    async def get_user_subscription_summary(self, user_id: int) -> str:
        """Получить сводку по подписке пользователя"""
        status = await self.db.get_user_subscription_status(user_id)
        stats = await self.db.get_user_stats(user_id)
        
        summary = f"📊 Ваша подписка:\n\n"
        summary += f"📦 План: {SUBSCRIPTION_PLANS.get(status['type'], {}).get('name', 'Неизвестно')}\n"
        
        if status['is_active']:
            summary += f"✅ Статус: Активна\n"
            summary += f"📅 Действует до: {status['end_date'].strftime('%d.%m.%Y')}\n"
        else:
            summary += f"❌ Статус: Неактивна\n"
        
        summary += f"📈 Консультаций использовано: {stats['consultations_count']}\n"
        
        plan_info = stats['plan_info']
        if plan_info.get('consultations_limit') == -1:
            summary += f"📊 Лимит: безлимит\n"
        else:
            limit = plan_info.get('consultations_limit', 0)
            summary += f"📊 Лимит: {limit} в месяц\n"
        
        return summary
