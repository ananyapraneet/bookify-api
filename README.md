# Bookify API

A production-oriented **SaaS backend for a service booking platform**, built with FastAPI and PostgreSQL.

The project is being developed incrementally with a focus on **backend engineering, API design, authentication, database architecture, testing, containerization, and DevOps practices**.

---

## 🚀 Project Status

**Current Stage: Stage 3 — Authentication ✅**

Implemented:

* User registration
* Secure password hashing using Argon2
* JWT-based authentication
* User login
* Protected `/auth/me` endpoint
* PostgreSQL persistence
* SQLAlchemy ORM
* Alembic database migrations
* Authentication unit tests
* Authentication API integration tests
* Dockerized PostgreSQL

The project is actively under development.

---

## 🏗️ Architecture

```text
                        ┌──────────────────┐
                        │     Client       │
                        │ Swagger / REST   │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │    FastAPI       │
                        │   API Layer      │
                        └────────┬─────────┘
                                 │
                  ┌──────────────┼──────────────┐
                  │              │              │
                  ▼              ▼              ▼
             ┌─────────┐   ┌──────────┐   ┌──────────┐
             │ Schemas │   │ Services │   │ Security │
             │ Pydantic│   │ Business │   │ JWT/Auth │
             └─────────┘   └──────────┘   └──────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │    SQLAlchemy    │
                        │       ORM        │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   PostgreSQL     │
                        │     Database     │
                        └──────────────────┘
```

---

## 🛠️ Tech Stack

### Backend

* Python 3
* FastAPI
* Uvicorn
* Pydantic
* Pydantic Settings

### Database

* PostgreSQL
* SQLAlchemy
* Alembic
* psycopg2

### Authentication & Security

* JWT
* `python-jose`
* Argon2 password hashing
* `pwdlib`

### Testing

* Pytest
* FastAPI TestClient
* HTTPX

### Infrastructure / DevOps

* Docker
* Docker Compose
* Git
* GitHub

---

## 📁 Project Structure

```text
saas-backend/
│
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── auth.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── database.py
│   │   └── dependencies.py
│   │
│   ├── models/
│   │   └── user.py
│   │
│   ├── schemas/
│   │   └── user.py
│   │
│   ├── services/
│   │   └── user.py
│   │
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── tests/
│   ├── test_auth.py
│   └── test_security.py
│
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🔐 Authentication

Bookify uses JWT-based authentication.

### Registration

```http
POST /auth/register
```

Example request:

```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

Passwords are never stored in plaintext. They are hashed using **Argon2** before being persisted in PostgreSQL.

Duplicate email addresses are rejected with:

```http
409 Conflict
```

---

### Login

```http
POST /auth/login
```

Example request:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Successful authentication returns:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

---

### Current User

```http
GET /auth/me
```

Requires a valid JWT bearer token.

Example:

```http
Authorization: Bearer <JWT>
```

---

## 🧪 Testing

The project currently contains unit and API integration tests covering authentication and security.

Run the complete test suite:

```bash
python -m pytest
```

Current test status:

```text
13 passed
```

Test coverage currently includes:

* Password hashing
* Password verification
* Incorrect password handling
* JWT creation
* JWT decoding
* Invalid JWT handling
* User registration
* Duplicate email registration
* Login success
* Invalid login credentials
* Protected endpoint authentication
* Authentication failure scenarios

---

## 🐘 Running PostgreSQL

PostgreSQL is configured through Docker Compose.

Start the database:

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

The application expects PostgreSQL configuration through environment variables.

---

## ⚙️ Environment Variables

Create a local `.env` file:

```env
POSTGRES_USER=bookify
POSTGRES_PASSWORD=your_password
POSTGRES_DB=bookify
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> **Important:** Never commit `.env` or production secrets to GitHub.

---

## ▶️ Running the API

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the PostgreSQL container:

```bash
docker compose up -d
```

Run database migrations:

```bash
alembic upgrade head
```

Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## 📚 API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## 🗺️ Roadmap

The project will evolve into a complete SaaS booking platform.

### Stage 1 — Project Initialization ✅

* FastAPI application
* Project structure
* Health endpoint
* Docker setup

### Stage 2 — Database Layer ✅

* PostgreSQL
* SQLAlchemy
* Alembic
* Database configuration

### Stage 3 — Authentication ✅

* User registration
* Password hashing
* JWT authentication
* Login
* Protected endpoints
* Authentication tests

### Stage 4 — Service Management 🚧

* Service/provider models
* Service CRUD APIs
* Provider management
* Role-based authorization

### Stage 5 — Booking System

* Booking model
* Availability management
* Booking creation
* Booking cancellation
* Booking status management

### Stage 6 — Production Engineering

* Redis
* Background jobs
* Structured logging
* Error handling
* Configuration management
* Health/readiness checks

### Stage 7 — DevOps & Cloud

* CI/CD with GitHub Actions
* Docker image
* AWS deployment
* Infrastructure as Code
* Monitoring
* Logging
* Production deployment architecture

---

## 🎯 Engineering Goals

This project is designed to demonstrate practical experience with:

* REST API development
* Backend architecture
* Authentication and authorization
* Relational database design
* Secure credential handling
* Automated testing
* Docker
* CI/CD
* Cloud infrastructure
* Observability
* Production deployment

The goal is to build the application progressively from a local backend into a **production-style SaaS platform**.

---

## 📌 Development Philosophy

The project is intentionally developed in stages.

Each stage introduces a focused set of capabilities, followed by:

1. Implementation
2. Local verification
3. Automated tests
4. Git commit
5. GitHub version control

This provides a clear development history and makes the repository useful as both a **portfolio project and an engineering learning exercise**.

