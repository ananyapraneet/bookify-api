from redis.asyncio import Redis
from redis.exceptions import RedisError

SERVICES_LIST_CACHE_KEY = "services:list"


async def invalidate_services_cache(redis: Redis) -> None:
    try:
        await redis.delete(SERVICES_LIST_CACHE_KEY)
    except RedisError:
        pass
