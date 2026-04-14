# Deadlock Leaderboard (StatTrack) - Workspace Context

## Project Overview
StatTrack is a real-time leaderboard and player statistics dashboard for Valve's game *Deadlock*. It implements a high-performance architecture to fetch, store, and serve player ranks and history.

### Core Architecture
- **Data Ingestion:** Celery Beat schedules periodic tasks to fetch live data from `deadlock-api.com`.
- **Storage Strategy (CQRS):** 
  - **Write Path:** Celery workers handle heavy PostgreSQL writes (upserts) and Redis sorted set updates.
  - **Read Path:** FastAPI serves low-latency requests directly from Redis (speed layer) and persistent data from PostgreSQL.
- **Real-Time Updates:** Redis Pub/Sub notifies FastAPI of data refreshes, which are then pushed to the React frontend via WebSockets.
- **Performance:** Uses Redis sorted sets (`ZSET`) for O(log N) leaderboard ranking and result caching with event-driven invalidation.

### Tech Stack
- **Backend:** FastAPI (Python 3.12+), Celery, Redis (Sorted Sets + Pub/Sub), PostgreSQL (SQLAlchemy + Alembic).
- **Frontend:** React (TypeScript + Vite), TailwindCSS, TanStack Query (Server State), Recharts (Rank Graphs).
- **Infrastructure:** Docker Compose for orchestration; GitHub Actions for CI/CD.

---

## Directory Structure
- `backend/`: FastAPI application, database models, and Celery tasks.
  - `routers/`: API endpoints (REST & WebSockets).
  - `services/`: Business logic (Cache management, API clients, Connection registry).
  - `alembic/`: Database migration scripts.
- `frontend/`: React application.
  - `src/components/`: Reusable UI components (Charts, Tables, Badges).
  - `src/hooks/`: Custom hooks for data fetching and WebSocket management.
  - `src/pages/`: Main views (Leaderboard, Player Profile).

---

## Development Workflow

### Prerequisites
- Docker & Docker Desktop
- Node.js 20+
- Python 3.12 (if running backend outside Docker)

### Essential Commands
| Action | Command |
| :--- | :--- |
| **Start All Services** | `docker compose up --build` |
| **Run Migrations** | `docker compose exec api alembic upgrade head` |
| **Seed Hero Data** | `docker compose exec api python seed.py` |
| **Backend Tests** | `docker compose exec api pytest tests/` |
| **Frontend Dev** | `cd frontend && npm install && npm run dev` |
| **Frontend Lint/Type** | `cd frontend && npm run lint && npx tsc --noEmit` |

### Manual Task Trigger
To force a leaderboard refresh immediately:
```bash
docker compose exec worker celery -A tasks call tasks.refresh_leaderboard --args='["NAmerica"]'
```

---

## Engineering Standards & Conventions

### Backend
- **Type Safety:** Use Pydantic schemas in `backend/schemas.py` for all request/response validation.
- **Concurrency:** Prefer `async/await` for I/O bound operations; use `run_async` helper for executing coroutines within synchronous Celery tasks.
- **Database:** Always use `on_conflict_do_update` (upserts) for player records to maintain idempotency in the ingestion pipeline.
- **Caching:** Implement cache-aside logic using the decorators/helpers in `backend/services/response_cache.py`.

### Frontend
- **State Management:** Use TanStack Query (React Query) for all server-side state. Do not use local `useState` for API data.
- **Styling:** Strictly follow the utility-first approach with TailwindCSS. Avoid custom CSS files unless necessary for complex animations.
- **WebSockets:** Use the `useLeaderboardSocket` hook to handle real-time updates and automatic reconnection.

### General
- **Environment Variables:** All configuration must be driven by `.env`. Never hardcode connection strings.
- **Validation:** Every feature addition must include corresponding tests in `backend/tests/` and pass the frontend type check.
