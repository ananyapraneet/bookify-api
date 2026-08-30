FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home --shell /bin/bash bookify

COPY --chown=bookify:bookify app ./app
COPY --chown=bookify:bookify alembic.ini .
COPY --chown=bookify:bookify alembic ./alembic

USER bookify

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
