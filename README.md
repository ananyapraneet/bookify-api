# Bookify API

A production-oriented **SaaS backend for a service booking platform**, built with FastAPI and PostgreSQL.

The project is being developed incrementally with a focus on **backend engineering, API design, authentication, authorization, database architecture, business logic, automated testing, caching, background processing,
containerization, and DevOps practices**.

---

## 🚀 Project Status

**Current Stage: Stage 9 — Background Processing with Celery ✅**

Implemented:

* FastAPI application
* PostgreSQL persistence
* SQLAlchemy ORM
* Alembic database migrations
* User registration
* Secure password hashing using Argon2
* JWT-based authentication
* User login
* Protected `/auth/me` endpoint
* User roles: Customer, Provider, Admin
* Role-based access control
* Service CRUD
* Provider ownership enforcement
* Admin service management
* Service input validation
* Booking creation
* Booking availability / overlap validation
* Booking cancellation
* Booking status management
* Provider booking management
* Customer booking restrictions
* Admin booking management
* Booking status transition rules
* Centralized exception handling
* Request validation error handling
* Structured application logging
* Liveness health check
* Database readiness check
* Redis integration
* Redis client configuration
* Redis health/readiness integration
* Cache abstraction
* Cache-aside pattern
* Service list caching
* Cache hit/miss handling
* Cache TTL strategy
* Cache invalidation after service mutations
* Cache consistency handling
* Redis failure handling
* Redis-related automated tests
* Cache performance benchmarking
* Celery integration
* Redis-backed Celery message broker
* Celery result backend
* Asynchronous background task processing
* Booking confirmation background task
* Celery task retry configuration
* Task failure handling
* Maximum retry handling
* Background task logging
* Celery task execution tests
* Booking-to-Celery task dispatch testing
* Dockerized FastAPI application
* Dockerized PostgreSQL
* Dockerized Redis
* Dockerized Celery worker
* Non-root container execution
* Production-oriented container configuration

**Test Status: 75 passed, 1 warning**

### Cache Performance Benchmark

A local performance comparison was performed between the database-backed cache-miss path and the Redis cache-hit path for `GET /services`.

| Metric   | Cache Miss / PostgreSQL | Cache Hit / Redis |
| -------- | ----------------------: | ----------------: |
| Requests |                      20 |                20 |
| Minimum  |                34.02 ms |          18.02 ms |
| Maximum  |               101.58 ms |          31.17 ms |
| Average  |            **41.15 ms** |      **22.17 ms** |
| Median   |                36.97 ms |          21.47 ms |

Measured results:

* **Latency reduction:** 46.13%
* **Approximate speedup:** 1.86×
* Benchmark environment: local development environment with PostgreSQL and Redis running through Docker

These results represent the difference between a forced cache-miss/database path and a Redis cache-hit path under the local test environment. Actual performance improvements will vary depending on deployment infrastructure, network 
latency, database load, dataset size, and application workload.

## The project is actively under development.

---

# 🏗️ Architecture

Bookify currently uses FastAPI for synchronous API processing, Redis for caching and Celery message brokering, PostgreSQL for persistence, and a dedicated Celery worker for asynchronous background processing.

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
                         ┌────────┴────────┐
                         │                 │
                         ▼                 ▼
                  ┌────────────┐    ┌────────────┐
                  │   Redis    │    │ SQLAlchemy │
                  │   Cache    │    │    ORM     │
                  └────────────┘    └──────┬─────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │    PostgreSQL    │
                                  │     Database     │
                                  └──────────────────┘

                         Background Processing
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      Redis       │
                         │   Celery Broker  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Celery Worker   │
                         │  Background Jobs │
                         └────────┬─────────┘
                                  │
                                  ▼
                           Task Execution
```

Redis has two distinct responsibilities in the current architecture:

```text
                    ┌──────────────────┐
                    │      Redis       │
                    └────────┬─────────┘
                             │
               ┌─────────────┴─────────────┐
               │                           │
               ▼                           ▼
        ┌──────────────┐            ┌──────────────┐
        │ Cache Layer  │            │ Celery Broker│
        │ Service Data │            │ Task Queue   │
        └──────────────┘            └──────┬───────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ Celery Worker   │
                                  └─────────────────┘
```

---

# ⚡ Caching Flow

Bookify uses a **cache-aside pattern** for frequently accessed service data.

```text
GET /services
      │
      ▼
   Redis GET
      │
      ├── Cache HIT ──────► Return cached services
      │
      └── Cache MISS
              │
              ▼
         PostgreSQL
              │
              ▼
        Store in Redis
              │
              ▼
        Return services
```

Service mutations invalidate the cached service list:

```text
Create / Update / Delete Service
              │
              ▼
        PostgreSQL
              │
              ▼
      Invalidate Redis
```

Redis is treated as an optimization rather than a hard dependency for service retrieval. If Redis becomes unavailable, service retrieval falls back to PostgreSQL.

---

# 🔄 Background Processing

Bookify uses **Celery** to process tasks asynchronously outside the main FastAPI request lifecycle.

The current architecture is:

```text
Client
   │
   ▼
FastAPI
   │
   ├── Normal API processing
   │
   └── Queue background task
            │
            ▼
       Redis Broker
            │
            ▼
      Celery Worker
            │
            ▼
       Task Execution
```

This allows potentially slow or non-critical work to be handled asynchronously without unnecessarily blocking the API request.

---

## Celery Components

### FastAPI

The API creates the booking and, after a successful database transaction, dispatches the background task.

### Redis Broker

Redis acts as the **Celery message broker**, holding queued tasks until a worker consumes them.

### Celery Worker

The Celery worker continuously listens to Redis and executes registered background tasks.

### Result Backend

Redis is also configured as the Celery result backend so task execution results and states can be tracked.

---

# 📩 Booking Confirmation Task

The first background workflow implemented in Bookify is booking confirmation processing.

The booking flow is:

```text
POST /bookings
       │
       ▼
Validate request
       │
       ▼
Create booking
       │
       ▼
Commit transaction
       │
       ▼
Queue confirmation task
       │
       ▼
Redis Broker
       │
       ▼
Celery Worker
       │
       ▼
Process confirmation
```

The important design principle is that the booking transaction is committed **before** the Celery task is queued.

This prevents a background task from being dispatched for a booking that ultimately fails to persist.

The current confirmation workflow simulates notification processing using application logging rather than an external email provider.

---

# 🔁 Celery Task Retries

Background tasks can fail because of temporary infrastructure or application problems.

Bookify uses Celery retry mechanisms to make background processing more resilient.

The general workflow is:

```text
Task
 ↓
Failure
 ↓
Retry
 ↓
Failure
 ↓
Retry
 ↓
Failure
 ↓
Maximum retries reached
 ↓
Task marked as failed
```

The Celery configuration includes:

* Automatic retry handling
* Retry delay
* Maximum retry attempts
* Failure logging
* Task execution logging

This demonstrates a more production-oriented approach to asynchronous processing than simply executing a background function once.

---

# 📊 Task Observability

Celery task execution is observable through application and worker logs.

Typical task lifecycle events include:

```text
Task received
Task started
Task completed
```

Failure scenarios can also produce retry and failure information:

```text
Task failed
Task retry scheduled
Task retrying
Maximum retries reached
```

Celery task states include:

```text
PENDING
STARTED
SUCCESS
FAILURE
RETRY
```

A dedicated monitoring interface such as Flower has intentionally not been added yet. The current implementation focuses on the core task processing architecture, retries, failure handling, logging, and automated testing.

---

# 🛠️ Tech Stack

## Backend

* Python 3
* FastAPI
* Uvicorn
* Pydantic
* Pydantic Settings

## Database

* PostgreSQL
* SQLAlchemy
* Alembic
* psycopg2

## Caching

* Redis
* `redis-py`
* Redis async client
* Cache-aside pattern
* TTL-based caching
* Cache invalidation

## Background Processing

* Celery
* Redis message broker
* Redis result backend
* Asynchronous task processing
* Task retries
* Failure handling
* Background task logging

## Authentication & Security

* JWT
* `python-jose`
* Argon2 password hashing
* `pwdlib`
* Role-based access control

## Testing

* Pytest
* FastAPI TestClient
* HTTPX
* Redis integration tests
* Celery task tests
* Failure-path tests
* Cache behavior tests
* Performance benchmarking

## Infrastructure / DevOps

* Docker
* Docker Compose
* Git
* GitHub

---

# 📁 Project Structure

```text
saas-backend/
│
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── health.py
│   │       ├── roles.py
│   │       ├── services.py
│   │       └── bookings.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── celery.py
│   │   ├── config.py
│   │   ├── redis.py
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
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── notifications.py
│   │
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── scripts/
│   └── benchmark_cache.py
│
├── tests/
│   ├── test_auth.py
│   ├── test_roles.py
│   ├── test_security.py
│   ├── test_services.py
│   ├── test_bookings.py
│   ├── test_celery.py
│   ├── test_health.py
│   └── test_redis.py
│
├── .dockerignore
├── .env
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🔐 Authentication

Bookify uses JWT-based authentication.

## Registration

```text
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

```text
409 Conflict
```

---

## Login

```text
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

```text
GET /auth/me
```

Requires a valid JWT bearer token.

```text
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

```text
GET /roles/customer
GET /roles/provider
GET /roles/admin
```

Users attempting to access an endpoint requiring a different role receive:

```text
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

```text
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

```text
GET /services
```

Authenticated users can retrieve available services.

The service list uses Redis caching with a cache-aside strategy.

On a cache hit, the API returns the serialized service data directly from Redis.

On a cache miss, the API retrieves the services from PostgreSQL and stores the result in Redis for subsequent requests.

---

## Get Service

```text
GET /services/{service_id}
```

Returns a specific service.

A non-existent service returns:

```text
404 Not Found
```

---

## Update Service

```text
PATCH /services/{service_id}
```

Authorization rules:

* Providers can update their own services.
* Providers cannot update another provider's service.
* Admins can update services owned by other providers.
* Customers cannot update services.

After a successful update, the service-list cache is invalidated to prevent stale cached data.

---

## Delete Service

```text
DELETE /services/{service_id}
```

Authorization rules:

* Providers can delete their own services.
* Providers cannot delete another provider's service.
* Admins can delete services owned by other providers.
* Customers cannot delete services.

After a successful deletion, the service-list cache is invalidated.

Unauthorized operations return:

```text
403 Forbidden
```

---

# ⚡ Redis / Caching

Bookify uses Redis to reduce database access for frequently requested service data.

## Redis Integration

Redis runs as a Docker Compose service:

```text
redis:7-alpine
```

The application connects to Redis through configurable environment variables.

Redis configuration includes:

* Host
* Port
* Database number

Redis is also used as the message broker and result backend for Celery background processing.

---

## Cache Key

The service list uses the following cache key:

```text
services:list
```

---

## TTL Strategy

Cached service data uses a **60-second TTL**.

This provides a balance between:

* Reducing repeated database queries
* Keeping cached data reasonably fresh
* Preventing indefinitely stale data

---

## Cache-Aside Pattern

The `/services` endpoint follows this flow:

```text
1. Check Redis
2. If cache hit → return cached data
3. If cache miss → query PostgreSQL
4. Serialize the result
5. Store result in Redis
6. Return response
```

---

## Cache Invalidation

The service cache is invalidated after:

```text
POST   /services
PATCH  /services/{service_id}
DELETE /services/{service_id}
```

This prevents the service-list cache from continuing to serve data that no longer reflects the database state.

---

## Redis Failure Handling

Redis is treated as an optimization rather than a hard dependency for service retrieval.

If Redis becomes unavailable:

* Cache reads fail gracefully.
* The application falls back to PostgreSQL.
* Cache writes fail gracefully.
* Service mutations continue to operate.
* Redis failures do not cause the service API to become unavailable.

This design prevents a cache outage from becoming a complete application outage.

---

## Redis Health / Readiness

The application checks Redis availability as part of the readiness health check.

Redis connectivity is verified using a Redis `PING`.

A healthy system reports Redis as available, while Redis failures are reported without crashing the application.

---

# 📊 Cache Performance Benchmark

A performance benchmark was added under:

```text
scripts/benchmark_cache.py
```

The benchmark compares:

1. **Cache-miss path** — request reaches PostgreSQL.
2. **Cache-hit path** — request is served from Redis.

### Results

20 requests were measured for each path.

| Metric  | Cache Miss / PostgreSQL | Cache Hit / Redis |
| ------- | ----------------------: | ----------------: |
| Minimum |                34.02 ms |          18.02 ms |
| Maximum |               101.58 ms |          31.17 ms |
| Average |            **41.15 ms** |      **22.17 ms** |
| Median  |                36.97 ms |          21.47 ms |

### Observed improvement

```text
Latency reduction: 46.13%
Approximate speedup: 1.86x
```

These measurements were collected locally with PostgreSQL and Redis running through Docker.

The benchmark demonstrates the performance characteristics of the cache-hit path relative to the database-backed cache-miss path. Production performance will depend on infrastructure, network latency, database workload, dataset 
size, and traffic patterns.

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

```text
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

After a successful booking transaction is committed, Bookify dispatches a booking confirmation task to Celery for asynchronous processing.

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

```text
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

# ❤️ Booking Confirmation Background Workflow

After a booking is successfully committed to PostgreSQL:

```text
Booking Created
      │
      ▼
Database Commit
      │
      ▼
Celery Task Dispatch
      │
      ▼
Redis Broker
      │
      ▼
Celery Worker
      │
      ▼
Booking Confirmation Processing
```

The API does not need to perform the confirmation processing synchronously as part of the booking request.

This separates the core booking transaction from secondary background work and allows the application to scale asynchronous processing independently.

---

# 🧪 Testing

The project contains automated tests covering authentication, security, role-based authorization, service CRUD, booking workflows, health checks, Redis integration, cache behavior, Celery background processing, and failure paths.

Run the complete test suite:

```bash
python -m pytest
```

Current test status:

```text
75 passed, 1 warning
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
* Service cache invalidation
* Redis cache hit handling
* Redis cache miss handling

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

### Redis / Caching

* Redis connectivity
* Redis unavailable failure handling
* Redis cache hit
* Redis cache miss
* Database fallback
* Service cache invalidation after creation
* Service cache invalidation after update
* Service cache invalidation after deletion

### Celery / Background Processing

* Celery application configuration
* Booking confirmation task registration
* Booking confirmation task execution
* Successful task execution
* Task retry configuration
* Task retry behavior after failure
* Maximum retry handling
* Booking flow dispatching the confirmation task

### Health / Failure Paths

* Liveness health check
* Database readiness
* Database unavailable handling
* Redis availability
* Redis failure handling

---

# 🩺 Health Checks

Bookify exposes liveness and readiness endpoints.

## Liveness

```text
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

The liveness endpoint confirms that the API process is running.

---

## Readiness

```text
GET /health/ready
```

The readiness endpoint verifies required infrastructure dependencies.

Example healthy response:

```json
{
  "status": "ok",
  "database": "ok",
  "redis": "ok"
}
```

A readiness failure does not crash the application. Instead, the endpoint reports the unavailable dependency.

---

# 🐘 Running PostgreSQL

PostgreSQL is configured through Docker Compose.

Start the infrastructure:

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

Expected services include:

```text
bookify-postgres
bookify-redis
bookify-api
bookify-celery-worker
```

---

# ⚡ Running Redis

Redis is included in `docker-compose.yml`.

Start Redis:

```bash
docker compose up -d redis
```

Verify the Redis container:

```bash
docker ps
```

Test Redis connectivity:

```bash
docker exec bookify-redis redis-cli ping
```

Expected:

```text
PONG
```

---

# 🔄 Running Celery

The Celery worker can be started locally using:

```bash
celery -A app.core.celery worker --loglevel=info
```

The worker connects to Redis as the message broker and discovers the registered Bookify background tasks.

The Docker Compose configuration also provides a dedicated Celery worker container.

---

# 🐳 Docker

Bookify uses Docker Compose to run the application infrastructure.

The current containerized architecture includes:

```text
┌───────────────────────┐
│      FastAPI API      │
│      bookify-api      │
└───────────┬───────────┘
            │
            ├─────────────────────┐
            │                     │
            ▼                     ▼
┌───────────────────────┐ ┌───────────────────────┐
│      PostgreSQL       │ │        Redis          │
│    bookify-postgres   │ │     bookify-redis     │
└───────────────────────┘ └───────────┬───────────┘
                                      │
                                      ▼
                            ┌───────────────────────┐
                            │    Celery Worker      │
                            │ bookify-celery-worker │
                            └───────────────────────┘
```

The FastAPI and Celery worker containers run as the non-root `bookify` user.

Verify the container user:

```bash
docker exec bookify-api whoami
```

Expected:

```text
bookify
```

The same applies to the Celery worker.

---

# ⚙️ Environment Variables

Create a local `.env` file:

```text
POSTGRES_USER=bookify
POSTGRES_PASSWORD=your_password
POSTGRES_DB=bookify
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> **Important:** Never commit `.env` or production secrets to GitHub.

---

# ▶️ Running the API Locally

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start PostgreSQL and Redis:

```bash
docker compose up -d postgres redis
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

# 🚀 Running the Full Docker Stack

Build and start the complete application:

```bash
docker compose up --build
```

This starts:

```text
FastAPI
PostgreSQL
Redis
Celery Worker
```

Verify the containers:

```bash
docker ps
```

The API should be available at:

```text
http://localhost:8000
```

---

# 📊 Running the Cache Benchmark

With PostgreSQL, Redis, and the FastAPI application running:

```bash
python scripts/benchmark_cache.py
```

The script requires a valid JWT access token and measures the service-list endpoint under cache-miss and cache-hit conditions.

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

* Stronger request/input validation
* Centralized error handling
* Structured application logging
* Consistent API error responses
* Liveness and readiness health checks
* Database health/readiness checks
* Production-oriented configuration
* Integration and failure-path tests

### Stage 8 — Redis / Caching ✅

* Redis integration
* Redis connection/client configuration
* Redis health/readiness integration
* Cache abstraction
* Cache-aside pattern
* Cache keys and TTL strategy
* Cache frequently accessed service data
* Cache hit/miss handling
* Cache invalidation
* Cache consistency considerations
* Redis failure handling
* Redis-related automated tests
* Performance comparison before/after caching

### Stage 9 — Background Processing with Celery ✅

* Celery integration
* Redis message broker
* Redis result backend
* Background task architecture
* Asynchronous task processing
* Booking confirmation workflow
* Celery worker
* Task registration and discovery
* Task retries
* Retry delays
* Maximum retry handling
* Task failure handling
* Background task logging
* Celery task tests
* Booking task dispatch testing
* Dockerized Celery worker

### Stage 10 — DevOps & Cloud

* CI/CD with GitHub Actions
* Production Docker image
* AWS deployment
* Infrastructure as Code
* Monitoring
* Centralized logging
* Production deployment architecture

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
* Redis and caching
* Cache-aside architecture
* Cache invalidation
* Failure-tolerant application design
* Celery background processing
* Asynchronous task architecture
* Redis-backed message queues
* Task retries and failure handling
* Docker
* Docker Compose
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
4. Performance or failure-path validation where applicable
5. Git commit
6. GitHub version control

This provides a clear development history and makes the repository useful as both a **portfolio project and an engineering learning exercise**.
