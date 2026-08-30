# Bookify API

A production-oriented **SaaS backend for a service booking platform**, built with FastAPI and PostgreSQL.

The project is being developed incrementally with a focus on **backend engineering, API design, authentication, authorization, database architecture, business logic, automated testing, containerization, and DevOps practices**.

---

## 🚀 Project Status

**Current Stage: Stage 7 — Production Quality ✅**

Implemented:

- FastAPI application
- PostgreSQL persistence
- SQLAlchemy ORM
- Alembic database migrations
- User registration
- Secure password hashing using Argon2
- JWT-based authentication
- User login
- Protected `/auth/me` endpoint
- User roles: Customer, Provider, Admin
- Role-based access control
- Service CRUD
- Provider ownership enforcement
- Admin service management
- Service input validation
- Booking creation
- Booking availability / overlap validation
- Booking cancellation
- Booking status management
- Provider booking management
- Customer booking restrictions
- Admin booking management
- Booking status transition rules
- Centralized exception handling
- Request validation error handling
- Structured application logging
- Liveness health check
- Database readiness check
- Failure-path testing
- Automated authentication, security, RBAC, service, booking, and health tests
- Dockerized PostgreSQL

**Test Status: 61 passed, 1 warning**

The project is actively under development.
---

## 🏗️ Architecture

```text
                        ┌──────────────────┐
                        │      Client      │
                        │   Swagger / REST │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │     FastAPI      │
                        │     API Layer    │
                        └────────┬─────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
         ┌────────────┐   ┌────────────┐   ┌────────────┐
         │  Schemas   │   │  Services  │   │  Security  │
         │  Pydantic  │   │  Business  │   │  JWT/RBAC  │
         └────────────┘   └──────┬─────┘   └────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │    SQLAlchemy    │
                        │       ORM        │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │    PostgreSQL    │
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
* Role-based access control

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
│   │       ├── auth.py
│   │       ├── roles.py
│   │       ├── services.py
│   │       └── bookings.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── database.py
│   │   └── dependencies.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── service.py
│   │   └── booking.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── service.py
│   │   └── booking.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── service.py
│   │   └── booking.py
│   │
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── tests/
│   ├── test_auth.py
│   ├── test_roles.py
│   ├── test_security.py
│   ├── test_services.py
│   └── test_bookings.py
│
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🔐 Authentication

Bookify uses JWT-based authentication.

## Registration

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

## Login

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

## Current User

```http
GET /auth/me
```

Requires a valid JWT bearer token.

```http
Authorization: Bearer <JWT>
```

---

# 👥 Role-Based Access Control

Bookify currently supports three user roles:

* **Customer**
* **Provider**
* **Admin**

Protected endpoints use the authenticated user's role to determine authorization.

## Role Endpoints

```http
GET /roles/customer
GET /roles/provider
GET /roles/admin
```

Users attempting to access an endpoint requiring a different role receive:

```http
403 Forbidden
```

---

# 🧾 Services

Services represent bookable offerings within the platform.

Each service contains:

* Name
* Description
* Price
* Duration in minutes
* Owner/provider ID
* Creation timestamp
* Update timestamp

## Create Service

```http
POST /services
```

Only **Providers and Admins** can create services.

Example request:

```json
{
  "name": "Premium Haircut",
  "description": "Haircut with styling",
  "price": 799.00,
  "duration_minutes": 45
}
```

---

## List Services

```http
GET /services
```

Authenticated users can retrieve available services.

---

## Get Service

```http
GET /services/{service_id}
```

Returns a specific service.

A non-existent service returns:

```http
404 Not Found
```

---

## Update Service

```http
PATCH /services/{service_id}
```

Authorization rules:

* Providers can update their own services.
* Providers cannot update another provider's service.
* Admins can update services owned by other providers.
* Customers cannot update services.

---

## Delete Service

```http
DELETE /services/{service_id}
```

Authorization rules:

* Providers can delete their own services.
* Providers cannot delete another provider's service.
* Admins can delete services owned by other providers.
* Customers cannot delete services.

Unauthorized operations return:

```http
403 Forbidden
```

---

# 📅 Booking System

Bookings connect customers with bookable services.

Each booking contains:

* Customer ID
* Service ID
* Booking date
* Start time
* End time
* Booking status
* Creation timestamp
* Update timestamp

## Create Booking

```http
POST /bookings
```

Only **Customers** can create bookings.

Example request:

```json
{
  "service_id": 1,
  "booking_date": "2026-09-15",
  "start_time": "10:00:00"
}
```

The booking duration is derived from the selected service.

---

## Booking Availability

The booking system prevents overlapping bookings for the same service.

An attempted overlapping booking is rejected rather than creating conflicting reservations.

---

## Booking Status

Bookings support the following statuses:

```text
pending
confirmed
completed
cancelled
```

Status transitions are controlled by business rules.

Examples:

```text
pending → confirmed
pending → cancelled
confirmed → completed
confirmed → cancelled
```

Completed bookings cannot be cancelled.

---

## Update Booking Status

```http
PATCH /bookings/{booking_id}/status
```

Authorization rules:

* Customers can only cancel their own bookings.
* Providers can manage bookings for their services.
* Admins can change booking statuses.
* Customers cannot confirm or complete bookings.
* Unauthorized providers cannot manage another provider's bookings.
* Invalid status transitions are rejected.

---

# 🧪 Testing

The project contains automated tests covering authentication, security, role-based authorization, service CRUD, and booking workflows.

Run the complete test suite:

```bash
python -m pytest
```

Current test status:

```text
52 passed, 1 warning
```

## Test Coverage

### Security

* Password hashing
* Password verification
* Incorrect password handling
* JWT creation
* JWT decoding
* Invalid JWT handling

### Authentication

* User registration
* Duplicate email registration
* Successful login
* Invalid login credentials
* Protected endpoint authentication
* Current-user retrieval
* Authentication failure scenarios

### Role-Based Authorization

* Customer role access
* Provider role access
* Admin role access
* Unauthorized role access
* Authentication requirements

### Service CRUD

* Provider service creation
* Customer creation rejection
* Service listing
* Service retrieval
* Non-existent service handling
* Provider updating own service
* Provider updating another provider's service rejection
* Admin updating another provider's service
* Provider deleting own service
* Provider deleting another provider's service rejection
* Admin deleting another provider's service
* Customer update/delete rejection
* Service price validation
* Service duration validation
* Required field validation
* Service authentication requirements

### Booking System

* Customer booking creation
* Provider booking creation rejection
* Booking authentication requirements
* Non-existent service handling
* Overlapping booking rejection
* Provider booking confirmation
* Provider booking completion
* Completed booking cancellation rejection
* Customer booking cancellation
* Customer status-change restrictions
* Provider booking cancellation
* Admin booking status management

---

# 🐘 Running PostgreSQL

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

# ⚙️ Environment Variables

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

# ▶️ Running the API

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start PostgreSQL:

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

# 📚 API Documentation

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

# 🗺️ Roadmap

The project will evolve into a complete production-style SaaS booking platform.

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
* User database model

### Stage 3 — Authentication ✅

* User registration
* Password hashing
* JWT authentication
* Login
* Protected `/auth/me` endpoint
* Authentication tests

### Stage 4 — Roles & Authorization ✅

* Customer role
* Provider role
* Admin role
* Role-based authorization
* Protected role endpoints
* Authorization tests

### Stage 5 — Services / Service CRUD ✅

* Service model
* Service schemas
* Service database migration
* Service CRUD service layer
* Service API routes
* Provider ownership enforcement
* Admin service management
* Role-based authorization for services
* Service validation
* Service CRUD tests

### Stage 6 — Booking System ✅

* Booking model
* Booking database migration
* Booking creation
* Service availability validation
* Overlapping booking prevention
* Booking cancellation
* Booking status management
* Status transition rules
* Provider booking management
* Customer booking restrictions
* Admin booking management
* Booking workflow tests

### Stage 7 — Production Quality ✅

- Stronger request/input validation
- Centralized error handling
- Structured application logging
- Consistent API error responses
- Liveness and readiness health checks
- Database health/readiness checks
- Production-oriented configuration
- Integration and failure-path tests

### Stage 8 — Redis / Caching

- Redis integration
- Redis connection/client configuration
- Redis health/readiness integration
- Cache abstraction
- Cache-aside pattern
- Cache keys and TTL strategy
- Cache frequently accessed service data
- Cache hit/miss handling
- Cache invalidation
- Cache consistency considerations
- Redis failure handling
- Redis-related automated tests
- Performance comparison before/after caching

### Stage 9 — Background Processing

- Background job architecture
- Asynchronous task processing
- Booking-related background workflows
- Job retries
- Failure handling
- Scheduled/background tasks

### Stage 10 — DevOps & Cloud

- CI/CD with GitHub Actions
- Production Docker image
- AWS deployment
- Infrastructure as Code
- Monitoring
- Centralized logging
- Production deployment architecture
---

# 🎯 Engineering Goals

This project is designed to demonstrate practical experience with:

* REST API development
* Backend architecture
* Authentication and authorization
* Role-based access control
* Relational database design
* SQLAlchemy ORM
* Database migrations
* Secure credential handling
* Business logic implementation
* Automated testing
* Docker
* Redis and caching
* Background processing
* CI/CD
* Cloud infrastructure
* Observability
* Production deployment

The goal is to progressively build the application from a local backend into a **production-style SaaS platform**.

---

# 📌 Development Philosophy

The project is intentionally developed in stages.

Each stage introduces a focused set of capabilities, followed by:

1. Implementation
2. Local verification
3. Automated tests
4. Git commit
5. GitHub version control

This provides a clear development history and makes the repository useful as both a **portfolio project and an engineering learning exercise**.

