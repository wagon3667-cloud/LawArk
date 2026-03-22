"""
Тесты для SubscriptionService.

Что проверяем:
- can_user_subscribe: невалидный план, повторный trial, апгрейд, новый юзер
- activate_subscription: остатки дней не сгорают при продлении
- format_subscription_info: корректный вывод текста
- get_plan_info: возвращает нужный план
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.services.subscription_service import SubscriptionService
from src.utils.config import SUBSCRIPTION_PLANS


def make_service(db_overrides: dict = None) -> SubscriptionService:
    """Создаёт SubscriptionService с замоканной базой данных."""
    db = AsyncMock()

    # Дефолтные значения — новый юзер без подписки
    db.get_or_create_user.return_value = {"trial_used": False}
    db.get_user_subscription_status.return_value = {
        "type": "none",
        "is_active": False,
        "end_date": None,
    }

    if db_overrides:
        for attr, value in db_overrides.items():
            setattr(db, attr, value)

    return SubscriptionService(db=db)


# ─── get_plan_info ────────────────────────────────────────────────────────────

def test_get_plan_info_valid():
    service = make_service()
    plan = service.get_plan_info("basic")
    assert plan["name"] == "Старт"
    assert plan["price"] == 299
    assert plan["duration_days"] == 30


def test_get_plan_info_invalid_returns_empty():
    service = make_service()
    plan = service.get_plan_info("nonexistent_plan")
    assert plan == {}


# ─── can_user_subscribe ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cannot_subscribe_to_invalid_plan():
    service = make_service()
    result = await service.can_user_subscribe(user_id=1, plan_type="phantom_plan")
    assert result["can_subscribe"] is False
    assert result["reason"] == "invalid_plan"


@pytest.mark.asyncio
async def test_cannot_take_trial_twice():
    db_overrides = {
        "get_or_create_user": AsyncMock(return_value={"trial_used": True}),
    }
    service = make_service(db_overrides)
    result = await service.can_user_subscribe(user_id=1, plan_type="trial")
    assert result["can_subscribe"] is False
    assert result["reason"] == "trial_used"


@pytest.mark.asyncio
async def test_new_user_can_take_trial():
    service = make_service()  # trial_used=False, нет активной подписки
    result = await service.can_user_subscribe(user_id=1, plan_type="trial")
    assert result["can_subscribe"] is True


@pytest.mark.asyncio
async def test_active_paid_user_can_upgrade():
    """Пользователь с активной подпиской может купить другой план — дни суммируются."""
    db_overrides = {
        "get_or_create_user": AsyncMock(return_value={"trial_used": False}),
        "get_user_subscription_status": AsyncMock(return_value={
            "type": "basic",
            "is_active": True,
            "end_date": datetime.now() + timedelta(days=10),
        }),
    }
    service = make_service(db_overrides)
    result = await service.can_user_subscribe(user_id=1, plan_type="unlimited")
    assert result["can_subscribe"] is True
    assert result.get("extend_active_plan") is True


@pytest.mark.asyncio
async def test_active_user_cannot_take_trial():
    """Активный пользователь не может взять повторный trial."""
    db_overrides = {
        "get_or_create_user": AsyncMock(return_value={"trial_used": False}),
        "get_user_subscription_status": AsyncMock(return_value={
            "type": "basic",
            "is_active": True,
            "end_date": datetime.now() + timedelta(days=5),
        }),
    }
    service = make_service(db_overrides)
    result = await service.can_user_subscribe(user_id=1, plan_type="trial")
    # Активная подписка + trial = нельзя (trial_used не нужен, логика выше)
    # Но trial_used=False и active=True → попадаем в блок "paid plans only"
    # Т.к. trial — не paid plan, падаем в "active_subscription"
    assert result["can_subscribe"] is False


# ─── activate_subscription ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_activate_invalid_plan_fails():
    service = make_service()
    result = await service.activate_subscription(user_id=1, plan_type="ghost")
    assert result["success"] is False


@pytest.mark.asyncio
async def test_activate_does_not_burn_remaining_days():
    """При продлении активной подписки оставшиеся дни не сгорают."""
    future_end = datetime.now() + timedelta(days=15)
    db_overrides = {
        "get_user_subscription_status": AsyncMock(return_value={
            "type": "basic",
            "is_active": True,
            "end_date": future_end,
        }),
    }
    service = make_service(db_overrides)
    result = await service.activate_subscription(user_id=1, plan_type="unlimited")

    assert result["success"] is True
    # Новая дата = future_end + 30 дней (duration unlimited)
    expected_expires = future_end + timedelta(days=SUBSCRIPTION_PLANS["unlimited"]["duration_days"])
    delta = abs((result["expires_at"] - expected_expires).total_seconds())
    assert delta < 5  # допуск 5 секунд


@pytest.mark.asyncio
async def test_activate_trial_marks_trial_used():
    """После активации trial выставляется флаг trial_used."""
    db_overrides = {
        "get_user_subscription_status": AsyncMock(return_value={
            "type": "none",
            "is_active": False,
            "end_date": None,
        }),
    }
    service = make_service(db_overrides)
    await service.activate_subscription(user_id=1, plan_type="trial")
    service.db.mark_trial_used.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_activate_paid_plan_saves_payment():
    """При активации платного плана записывается платёж."""
    service = make_service()
    await service.activate_subscription(user_id=1, plan_type="basic")
    service.db.add_subscription_payment.assert_called_once()


@pytest.mark.asyncio
async def test_activate_trial_does_not_save_payment():
    """Trial бесплатный — платёж не записывается."""
    service = make_service()
    await service.activate_subscription(user_id=1, plan_type="trial")
    service.db.add_subscription_payment.assert_not_called()


# ─── format_subscription_info ─────────────────────────────────────────────────

def test_format_subscription_info_contains_plan_name():
    service = make_service()
    text = service.format_subscription_info("basic")
    assert "Старт" in text
    assert "299" in text
    assert "30" in text


def test_format_subscription_info_unlimited_label():
    service = make_service()
    text = service.format_subscription_info("unlimited")
    assert "безлимит" in text


def test_format_subscription_info_unknown_plan():
    service = make_service()
    text = service.format_subscription_info("unknown")
    assert "Неизвестный план" in text
