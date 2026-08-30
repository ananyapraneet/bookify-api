from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.db.dependencies import get_db


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_readiness_check():
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "ok",
    }


def test_readiness_check_database_unavailable():
    def broken_db():
        class BrokenDB:
            def execute(self, query):
                raise SQLAlchemyError("Database unavailable")

        yield BrokenDB()

    app.dependency_overrides[get_db] = broken_db

    try:
        response = client.get("/health/ready")

        assert response.status_code == 503
        assert response.json() == {
            "detail": {
                "status": "degraded",
                "database": "unavailable",
            }
        }

    finally:
        app.dependency_overrides.clear()
