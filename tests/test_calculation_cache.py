import asyncio
from unittest.mock import AsyncMock

from redis import RedisError

import app.main as main
from app.data.calculation_cache import CalculationCache
from app.schemas import CalculationRequest


SERIES = " TEST-01 "
PARAMETERS = "/ 1000 / 700 / 400 /"


def run_calculate() -> dict[str, int | float]:
    request = CalculationRequest(series=SERIES, parameters=PARAMETERS)
    return asyncio.run(main.calculate_cost(request))


def test_cache_key_uses_normalized_request_values() -> None:
    cache = CalculationCache(AsyncMock(), ttl_seconds=60)

    normalized_key = cache._build_key("TEST-01", "1000/700/400")
    unnormalized_key = cache._build_key(SERIES, PARAMETERS)

    assert unnormalized_key == normalized_key
    assert normalized_key.startswith("calculation:v1:")


def test_cache_returns_zero_as_a_valid_value() -> None:
    redis = AsyncMock()
    redis.get.return_value = "0"
    cache = CalculationCache(redis, ttl_seconds=60)

    result = asyncio.run(cache.get(SERIES, PARAMETERS))

    assert result == 0.0


def test_cache_miss_returns_none() -> None:
    redis = AsyncMock()
    redis.get.return_value = None
    cache = CalculationCache(redis, ttl_seconds=60)

    result = asyncio.run(cache.get(SERIES, PARAMETERS))

    assert result is None


def test_cache_ignores_redis_read_errors() -> None:
    redis = AsyncMock()
    redis.get.side_effect = RedisError("Redis is unavailable")
    cache = CalculationCache(redis, ttl_seconds=60)

    result = asyncio.run(cache.get(SERIES, PARAMETERS))

    assert result is None


def test_cache_ignores_invalid_cached_value() -> None:
    redis = AsyncMock()
    redis.get.return_value = "not-a-number"
    cache = CalculationCache(redis, ttl_seconds=60)

    result = asyncio.run(cache.get(SERIES, PARAMETERS))

    assert result is None


def test_cache_set_uses_configured_ttl() -> None:
    redis = AsyncMock()
    cache = CalculationCache(redis, ttl_seconds=123)

    asyncio.run(cache.set(SERIES, PARAMETERS, 456.5))

    redis.set.assert_awaited_once_with(
        cache._build_key(SERIES, PARAMETERS),
        "456.5",
        ex=123,
    )


def test_cache_ignores_redis_write_errors() -> None:
    redis = AsyncMock()
    redis.set.side_effect = RedisError("Redis is unavailable")
    cache = CalculationCache(redis, ttl_seconds=60)

    asyncio.run(cache.set(SERIES, PARAMETERS, 456.5))


def test_calculate_returns_redis_hit_without_database_or_calculation(
    monkeypatch,
) -> None:
    cache_get = AsyncMock(return_value=0.0)
    cache_set = AsyncMock()
    database_get = AsyncMock()
    calculate = AsyncMock()
    monkeypatch.setattr(main.calculation_cache, "get", cache_get)
    monkeypatch.setattr(main.calculation_cache, "set", cache_set)
    monkeypatch.setattr(
        main.repository,
        "get_calculated_product_cost_async",
        database_get,
    )
    monkeypatch.setattr(main.calc_controller, "calculation", calculate)

    result = run_calculate()

    assert result == {"cost": 0.0}
    cache_get.assert_awaited_once_with(SERIES, PARAMETERS)
    cache_set.assert_not_awaited()
    database_get.assert_not_awaited()
    calculate.assert_not_awaited()


def test_database_hit_populates_redis_and_skips_calculation(monkeypatch) -> None:
    cache_get = AsyncMock(return_value=None)
    cache_set = AsyncMock()
    database_get = AsyncMock(return_value=1234)
    calculate = AsyncMock()
    monkeypatch.setattr(main.calculation_cache, "get", cache_get)
    monkeypatch.setattr(main.calculation_cache, "set", cache_set)
    monkeypatch.setattr(
        main.repository,
        "get_calculated_product_cost_async",
        database_get,
    )
    monkeypatch.setattr(main.calc_controller, "calculation", calculate)

    result = run_calculate()

    assert result == {"cost": 1234}
    cache_set.assert_awaited_once_with(SERIES, PARAMETERS, 1234)
    calculate.assert_not_awaited()


def test_calculated_value_is_written_to_redis(monkeypatch) -> None:
    cache_get = AsyncMock(return_value=None)
    cache_set = AsyncMock()
    database_get = AsyncMock(return_value=None)
    calculate = AsyncMock(return_value=2345.5)
    monkeypatch.setattr(main.calculation_cache, "get", cache_get)
    monkeypatch.setattr(main.calculation_cache, "set", cache_set)
    monkeypatch.setattr(
        main.repository,
        "get_calculated_product_cost_async",
        database_get,
    )
    monkeypatch.setattr(main.calc_controller, "calculation", calculate)

    result = run_calculate()

    assert result == {"cost": 2345.5}
    calculate.assert_awaited_once_with(SERIES, PARAMETERS)
    cache_set.assert_awaited_once_with(SERIES, PARAMETERS, 2345.5)
