import redis

DEFAULT_THRESHOLD = 100
KEY_PREFIX = "limit:user_id"


class RateLimiter:
    def __init__(self, client: redis.Redis, threshold: int = DEFAULT_THRESHOLD):
        self._client = client
        self._threshold = threshold

    def _key(self, user_id: str) -> str:
        return f"{KEY_PREFIX}:{user_id}"

    def is_allowed(self, user_id: str) -> bool:
        key = self._key(user_id)
        count = self._client.incr(key)
        if count == 1:
            self._client.expire(key, 60)
        return count <= self._threshold

    def current_usage(self, user_id: str) -> int:
        val = self._client.get(self._key(user_id))
        return int(val) if val else 0
