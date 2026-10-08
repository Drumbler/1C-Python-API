import hashlib

import logging
from redis import RedisError

from app.data.normalizer import normalize_calculated_product_parameters, normalize_calculated_product_series

logger = logging.getLogger(__name__)

class CalculationCache:
    def __init__(self, redis_client, ttl_seconds: int):
        self.redis = redis_client
        self.ttl_seconds = ttl_seconds

    def _build_key(self, series: str, parameters: str) -> str:
        normalized_series = normalize_calculated_product_series(series)
        normalized_parameters = normalize_calculated_product_parameters(parameters)

        raw_key = f"{normalized_series}\0{normalized_parameters}"
        key_hash = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
        return f"calculation:v1:{key_hash}"

    async def get(self, series: str, parameters: str):
        try:
            key = self._build_key(series, parameters)
            cached_value = await self.redis.get(key)

            if cached_value is None:
                return None
            
            return float(cached_value)
        except RedisError:
            logger.warning("Failed to read calculation cache", exc_info=True)
            return None

    async def set(self, series: str, parameters: str, cost: int | float) -> None:
        try:
            key = self._build_key(series, parameters)
            await self.redis.set(key, str(cost), ex=self.ttl_seconds)
        except RedisError:
            logger.warning("Failed to write calculation cache", exc_info=True)

