# My Bank

**My Bank** is a full-stack banking simulation built to showcase system design, design patterns, and pragmatic engineering trade-offs. It pairs a FastAPI backend with a React + Vite frontend, modeling real banking flows like onboarding, account management, and money transfers with strong attention to correctness and resilience.

## Highlights

- User registration, login, and token refresh with JWT access/refresh tokens.
- Checking and savings accounts with balances, status, and history.
- Money transfers with validation, authorization, and atomic balance updates.
- Idempotency on write endpoints to support safe retries.
- A modern dashboard UI with rich state handling and graceful error states.

## Architecture at a glance

| Layer        | Purpose                                          | Location                   |
| ------------ | ------------------------------------------------ | -------------------------- |
| API          | FastAPI routers, request validation, auth wiring | `backend/src/api/v1`       |
| Services     | Business logic and transaction orchestration     | `backend/src/services`     |
| Repositories | Data access abstractions                         | `backend/src/repositories` |
| Models       | SQLAlchemy models and database setup             | `backend/src/db`           |
| Schemas      | Pydantic DTOs for IO contracts                   | `backend/src/schemas`      |
| UI           | React pages, components, and services            | `frontend/src`             |

## Design patterns & engineering practices

- **Repository pattern** for data access isolation (`repositories/`).
- **Service layer** to centralize business rules (`services/`).
- **Dependency injection** via FastAPI dependencies for auth and DB sessions.
- **Idempotency decorator** to safely retry mutations (`core/idempotency.py`).
- **Token lifecycle management** with refresh token rotation and revocation.
- **Pessimistic locking + atomic updates** for transfer safety and consistency.
- **Frontend request deduplication** and idempotency keys for UX stability.

## Tech stack

| Area     | Tech                                                   |
| -------- | ------------------------------------------------------ |
| Backend  | FastAPI, SQLAlchemy, Pydantic, SQLite                  |
| Auth     | JWT access/refresh, Argon2 password hashing (`pwdlib`) |
| Frontend | React 19, Vite, Tailwind CSS, React Router             |
| Tooling  | TypeScript, ESLint, Prettier                           |

## Running locally

### Backend

1. Install dependencies with uv:
   ```bash
   uv sync --frozen
   ```
2. Start the API:
   ```bash
   uv run uvicorn src.main:app --reload
   ```

The API defaults to SQLite at `sqlite:///./test.db` (see `.env`).

### Frontend

1. Install and run:
   ```bash
   npm install
   npm run dev
   ```

Open `http://localhost:5173`.

### Docker

```bash
docker compose up --build
```

Frontend runs at `http://localhost:5173` and the API at `http://localhost:8000`.

## API overview

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/token/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/users/me`
- `GET /api/v1/accounts`
- `POST /api/v1/accounts`
- `GET /api/v1/transactions`
- `POST /api/v1/transactions`

## Project structure

```
backend/
  src/
    api/            # HTTP endpoints
    core/           # config, security, idempotency
    db/             # models + DB setup
    repositories/   # data access
    schemas/        # request/response DTOs
    services/       # business logic
frontend/
  src/
    components/
    pages/
    services/
    types/
```
