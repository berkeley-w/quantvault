## QuantVault

QuantVault is a small trading and portfolio analytics platform built with **FastAPI** (backend) and **React + TypeScript + Vite** (frontend). The backend exposes a JSON API under `/api/*`, and the frontend is built to `frontend/dist/` and served by FastAPI in production.

### Backend

- **Stack**: FastAPI, SQLAlchemy, Alembic, SQLite (default), Pydantic v2
- **App entrypoint**: `backend/main.py`
- **Database models**: `backend/models.py`
- **Auth**: JWT-based auth with users table and roles (admin/trader)
- **Migrations**: Alembic under `backend/alembic/`

### Frontend

- **Stack**: React 18, TypeScript, Vite, Tailwind (via `@tailwindcss/vite`)
- **Source**: `frontend/src/`
- **Build output**: `frontend/dist/`

---

## Setup Instructions

### Prerequisites

- Python 3.12
- Node.js 20+

### Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file based on the example:

```bash
cp .env.example .env
```

Edit `.env` (or set environment variables) as needed:

- `DATABASE_URL` – e.g. `sqlite:///./quantvault.db`
- `ALPHA_VANTAGE_API_KEY` – your Alpha Vantage API key
- `JWT_SECRET` – strong random string
- `JWT_EXPIRY_HOURS` – default `24`

Run database migrations:

```bash
cd backend
alembic upgrade head
```

Start the backend locally:

```bash
cd backend
uvicorn main:app --reload
```

Health check:

- `GET http://localhost:8000/health`

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies `/api` and `/health` to `http://localhost:8000` (see `frontend/vite.config.ts`).

Build the frontend:

```bash
cd frontend
npm run build
```

---

## Authentication

- Users are stored in the `users` table (see `backend/models.py`).
- JWTs are issued and validated with `backend/services/auth.py`.
- Config is in `backend/config.py` (`JWT_SECRET`, `JWT_EXPIRY_HOURS`).
- Auth routes are in `backend/routers/auth.py` under `/api/auth/*`.

Key endpoints:

- `POST /api/auth/setup` – bootstrap first admin user (only works when no users exist)
- `POST /api/auth/register` – register a new trader user and return a JWT
- `POST /api/auth/login` – login with username/password and return a JWT
- `GET /api/auth/me` – returns current user info (requires `Authorization: Bearer <token>`)

All `/api/*` routes **except**:

- `POST /api/auth/login`
- `POST /api/auth/register`
- `POST /api/auth/setup`
- `GET /health`

require a valid Bearer token.

On the frontend:

- `AuthContext` in `frontend/src/contexts/AuthContext.tsx` manages auth state.
- `apiClient` in `frontend/src/api/client.ts` attaches `Authorization: Bearer <token>` to requests and redirects to `/login` on `401`.
- Login and registration flows are implemented in:
  - `frontend/src/pages/LoginPage.tsx`
  - `frontend/src/pages/RegisterPage.tsx`
- `ProtectedRoute` in `frontend/src/components/auth/ProtectedRoute.tsx` guards all protected routes.

---

## Running Tests

Backend tests use `pytest` and FastAPI's `TestClient`.

```bash
cd backend
pytest
```

Configuration:

- `backend/pytest.ini`
- Tests live under `backend/tests/`

Tests cover:

- Auth flow (setup, register, login, protected routes)
- CRUD for securities, traders, trades
- Restricted list behaviour
- Holdings computation

---

## Docker

A two-stage Dockerfile builds the frontend and runs the backend:

```bash
docker build -t quantvault .
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./quantvault.db \
  -e ALPHA_VANTAGE_API_KEY=your_key_here \
  -e JWT_SECRET=your_secret \
  quantvault
```

For local development with Docker Compose:

```bash
docker-compose up --build
```

Key files:

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

---

## Render Deployment

Render is configured via `render.yaml` at the repo root. It uses the Dockerfile and sets:

- `DATABASE_URL`
- `ALPHA_VANTAGE_API_KEY` (marked `sync: false`)
- `JWT_SECRET` (auto-generated)
- `PORT=8000`

Render health check path: `/health`.

---

## Verification Checklist

1. **Database** – `alembic upgrade head` creates all tables (including `users`).
2. **Admin setup** – `POST /api/auth/setup` creates the first admin and returns a token.
3. **Login** – `POST /api/auth/login` with valid credentials returns a token.
4. **Protection** – `/api/*` routes (except auth + `/health`) require a valid Bearer token.
5. **Frontend auth** – unauthenticated users see the login page; after login, all app pages work.
6. **Docker** – `docker build .` and `docker-compose up` start the app on `http://localhost:8000`.
7. **Tests** – `cd backend && pytest` passes.

