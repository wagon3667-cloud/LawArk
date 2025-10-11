import aiosqlite
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from ..utils.config import DATABASE_PATH, SUBSCRIPTION_PLANS

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    subscription_type TEXT DEFAULT 'trial',
                    subscription_end TIMESTAMP,
                    trial_used BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица консультаций
            await db.execute("""
                CREATE TABLE IF NOT EXISTS consultations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    question TEXT,
                    answer TEXT,
                    consultation_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица подписок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    plan_type TEXT,
                    amount INTEGER,
                    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            await db.commit()

    async def get_or_create_user(self, user_id: int, username: str = None) -> Dict[str, Any]:
        """Получить или создать пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            user = await cursor.fetchone()
            
            if not user:
                # Создаем нового пользователя с пробным периодом
                trial_end = datetime.now() + timedelta(days=7)
                await db.execute(
                    """INSERT INTO users (user_id, username, subscription_type, subscription_end)
                       VALUES (?, ?, 'trial', ?)""",
                    (user_id, username, trial_end)
                )
                await db.commit()
                
                cursor = await db.execute(
                    "SELECT * FROM users WHERE user_id = ?", (user_id,)
                )
                user = await cursor.fetchone()
            
            return dict(user)

    async def update_user_subscription(self, user_id: int, subscription_type: str, days: int):
        """Обновить подписку пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            subscription_end = datetime.now() + timedelta(days=days)
            await db.execute(
                """UPDATE users SET subscription_type = ?, subscription_end = ?
                   WHERE user_id = ?""",
                (subscription_type, subscription_end, user_id)
            )
            await db.commit()

    async def mark_trial_used(self, user_id: int):
        """Отметить пробный период как использованный"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET trial_used = 1 WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()

    async def add_consultation(self, user_id: int, question: str, answer: str, consultation_type: str):
        """Добавить консультацию"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO consultations (user_id, question, answer, consultation_type)
                   VALUES (?, ?, ?, ?)""",
                (user_id, question, answer, consultation_type)
            )
            await db.commit()

    async def add_subscription_payment(self, user_id: int, plan_type: str, amount: int):
        """Добавить запись об оплате подписки"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO subscriptions (user_id, plan_type, amount) VALUES (?, ?, ?)",
                (user_id, plan_type, amount)
            )
            await db.commit()

    async def get_user_consultations_count(self, user_id: int, days: int = 30) -> int:
        """Получить количество консультаций пользователя за период"""
        async with aiosqlite.connect(self.db_path) as db:
            since_date = datetime.now() - timedelta(days=days)
            cursor = await db.execute(
                """SELECT COUNT(*) FROM consultations 
                   WHERE user_id = ? AND created_at >= ?""",
                (user_id, since_date)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def get_user_subscription_status(self, user_id: int) -> Dict[str, Any]:
        """Получить статус подписки пользователя"""
        user = await self.get_or_create_user(user_id)
        
        subscription_end = datetime.fromisoformat(user['subscription_end']) if user['subscription_end'] else None
        is_active = subscription_end and subscription_end > datetime.now()
        
        return {
            'type': user['subscription_type'],
            'is_active': is_active,
            'end_date': subscription_end,
            'trial_used': bool(user['trial_used'])
        }

    async def can_user_consult(self, user_id: int) -> Dict[str, Any]:
        """Проверить, может ли пользователь получить консультацию"""
        status = await self.get_user_subscription_status(user_id)
        consultations_count = await self.get_user_consultations_count(user_id)
        
        if not status['is_active']:
            return {
                'can_consult': False,
                'reason': 'subscription_expired',
                'message': 'Подписка истекла'
            }
        
        # Проверяем лимит консультаций
        plan_type = status['type']
        if plan_type in SUBSCRIPTION_PLANS:
            limit = SUBSCRIPTION_PLANS[plan_type]['consultations_limit']
            if limit != -1 and consultations_count >= limit:
                return {
                    'can_consult': False,
                    'reason': 'consultations_limit',
                    'message': f'Превышен лимит консультаций ({limit} в месяц)'
                }
        
        return {
            'can_consult': True,
            'consultations_used': consultations_count,
            'consultations_limit': SUBSCRIPTION_PLANS.get(plan_type, {}).get('consultations_limit', -1)
        }

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        consultations_count = await self.get_user_consultations_count(user_id)
        subscription_status = await self.get_user_subscription_status(user_id)
        
        return {
            'consultations_count': consultations_count,
            'subscription': subscription_status,
            'plan_info': SUBSCRIPTION_PLANS.get(subscription_status['type'], {})
        }
