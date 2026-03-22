"""
Тесты для вспомогательных функций в config.py.

Чистые функции — тестируются без моков и БД.
"""
from src.utils.config import (
    _normalize_provider_name,
    _detect_provider,
    _extract_yandex_project_id,
    SUBSCRIPTION_PLANS,
)


# ─── _normalize_provider_name ─────────────────────────────────────────────────

def test_normalize_openai_alias():
    assert _normalize_provider_name("openai") == "openai_compatible"

def test_normalize_proxy_api_with_dash():
    assert _normalize_provider_name("proxy-api") == "proxyapi"

def test_normalize_case_insensitive():
    assert _normalize_provider_name("ProxyAPI") == "proxyapi"

def test_normalize_strips_whitespace():
    assert _normalize_provider_name("  proxyapi  ") == "proxyapi"

def test_normalize_unknown_stays_as_is():
    assert _normalize_provider_name("deepseek") == "deepseek"


# ─── _detect_provider ─────────────────────────────────────────────────────────

def test_detect_proxyapi_from_url():
    assert _detect_provider("https://api.proxyapi.ru/openai/v1", "gpt-4o") == "proxyapi"

def test_detect_yandex_from_model():
    assert _detect_provider("https://ai.api.cloud.yandex.net/v1", "gpt://my_project/yandexgpt/latest") == "yandex"

def test_detect_yandex_from_url():
    assert _detect_provider("https://yandex.cloud/v1", "some-model") == "yandex"

def test_detect_openai_compatible_fallback():
    assert _detect_provider("https://api.deepseek.com/v1", "deepseek-chat") == "openai_compatible"


# ─── _extract_yandex_project_id ───────────────────────────────────────────────

def test_extract_yandex_project_id_valid():
    model = "gpt://my_project_id/yandexgpt/latest"
    assert _extract_yandex_project_id(model) == "my_project_id"

def test_extract_yandex_project_id_no_prefix():
    assert _extract_yandex_project_id("gpt-4o") == ""

def test_extract_yandex_project_id_empty():
    assert _extract_yandex_project_id("") == ""

def test_extract_yandex_project_id_no_slash_after_prefix():
    assert _extract_yandex_project_id("gpt://noslash") == ""


# ─── SUBSCRIPTION_PLANS structure ────────────────────────────────────────────

def test_all_plans_have_required_keys():
    required = {"name", "duration_days", "price", "consultations_limit"}
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        assert required.issubset(plan.keys()), f"Plan '{plan_id}' missing keys"

def test_trial_is_free():
    assert SUBSCRIPTION_PLANS["trial"]["price"] == 0

def test_unlimited_has_no_consultation_limit():
    assert SUBSCRIPTION_PLANS["unlimited"]["consultations_limit"] == -1

def test_basic_has_consultation_limit():
    assert SUBSCRIPTION_PLANS["basic"]["consultations_limit"] > 0
