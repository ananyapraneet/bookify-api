from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.redis import get_redis
from app.db.dependencies import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check():
    return {
        "status": "ok",
    }


@router.get("/ready")
async def readiness_check(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    database_ok = False
    redis_ok = False

    try:
        db.execute(text("SELECT 1"))
        database_ok = True
    except SQLAlchemyError:
        pass

    try:
        await redis.ping()
        redis_ok = True
    except RedisError:
        pass
    finally:
        await redis.aclose()

    if database_ok and redis_ok:
        return {
            "status": "ok",
            "database": "ok",
            "redis": "ok",
        }

    detail = {
        "status": "degraded",
        "database": "ok" if database_ok else "unavailable",
        "redis": "ok" if redis_ok else "unavailable",
    }

    raise HTTPException(
        status_code=503,
        detail=detail,
    )
