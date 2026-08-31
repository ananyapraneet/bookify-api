import pytest

from app.core.redis import get_redis


@pytest.mark.asyncio
async def test_redis_connection():

    redis = get_redis()

    try:
        result = await redis.ping()
        assert result is True
    finally:
        await redis.aclose()


def test_redis_unavailable():
    from fastapi.testclient import TestClient
    from redis.exceptions import RedisError

    from app.api.routes.health import get_redis
    from app.main import app

    async def mock_get_redis():
        class FakeRedis:
            async def ping(self):
                raise RedisError("Redis unavailable")

            async def aclose(self):
                pass

        return FakeRedis()

    app.dependency_overrides[get_redis] = mock_get_redis

    try:
        client = TestClient(app)

        response = client.get("/health/ready")

        assert response.status_code == 503

        data = response.json()

        assert data["detail"]["status"] == "degraded"
        assert data["detail"]["redis"] == "unavailable"
    finally:
        app.dependency_overrides.clear()
