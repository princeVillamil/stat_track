# Deadlock Leaderboard

<img width="843" height="532" alt="image" src="https://github.com/user-attachments/assets/9959afc8-7fd4-4fa8-b6f7-82483a04b4b4" />


A real-time leaderboard and player stats dashboard for the game Deadlock. Fetches live data from `deadlock-api.com`, stores rank history in PostgreSQL, serves fast reads from Redis sorted sets, and pushes live updates to the browser via WebSockets.

---

## What it does

- **Live leaderboard** — top 1000+ players per region, updated every 5 minutes
- **Rank history** — tracks how a player's rank changes over time and graphs it
- **Hero stats** — shows which heroes each top player favors
- **Real-time updates** — WebSocket connection pushes rank changes to the browser the moment Celery finishes a refresh
- **Multi-region** — NAmerica, Europe, Asia, SAmerica, Oceania

---

## Architecture

```
deadlock-api.com
      │
      │  HTTP (every 5 min via Celery Beat)
      ▼
Celery Worker
      │
      ├──▶ PostgreSQL     — rank history, player records, heroes
      │    (write path)
      │
      ├──▶ Redis          — sorted sets for instant leaderboard reads
      │    (speed layer)     metadata cache, response cache
      │
      └──▶ Redis Pub/Sub  — notifies FastAPI of new data
                │
                ▼
           FastAPI
           ├── REST API   — leaderboard, players, heroes endpoints
           └── WebSocket  — pushes live updates to browser
                │
                ▼
           React Frontend
           ├── TanStack Query  — REST data fetching + caching
           ├── WebSocket hook  — live updates with auto-reconnect
           └── Recharts        — rank history graphs
```

### System design patterns used

| Pattern | Where |
|---|---|
| CQRS | Celery writes, FastAPI only reads |
| Cache-aside | Redis response cache with TTL + event invalidation |
| Pub/Sub | Redis channel notifies WebSocket clients of updates |
| Sorted sets | Redis `ZADD`/`ZREVRANGE` for O(log N) rank queries |
| Task queue | Celery + Beat for scheduled background ingestion |
| Idempotent writes | Postgres `INSERT ... ON CONFLICT DO UPDATE` |
| Pipeline batching | Redis pipeline sends all metadata reads in one round trip |
| Horizontal scaling | API and worker are separate containers, independently scalable |

---

## Tech stack

**Backend**
- FastAPI — async Python API framework
- Celery — distributed task queue for background jobs
- Celery Beat — scheduler that fires tasks on a cron-like schedule
- PostgreSQL — persistent storage for rank history and player data
- Redis — in-memory sorted sets, cache, and pub/sub message bus
- SQLAlchemy — ORM for database access
- Alembic — database migration tool
- httpx — async HTTP client for deadlock-api.com
- tenacity — retry logic with exponential backoff

**Frontend**
- React + TypeScript — UI framework
- Vite — build tool and dev server
- TanStack Query — server state management (fetching, caching, refetching)
- React Router — client-side routing
- Recharts — rank history line charts
- TailwindCSS — utility-first styling

**Infrastructure**
- Docker + Docker Compose — local development environment
- GitHub Actions — CI/CD pipeline (test + deploy on every push)
- Railway — backend hosting (API, worker, beat, Postgres, Redis)
- Vercel — frontend hosting
- Sentry — error tracking
- UptimeRobot — uptime monitoring

---

## Project structure

```
statTrack/
├── .github/
│   └── workflows/
│       ├── ci.yml          ← runs tests on every push
│       └── deploy.yml      ← deploys to Railway + Vercel on merge to main
├── backend/
│   ├── main.py             ← FastAPI app entry point, lifespan, CORS
│   ├── models.py           ← SQLAlchemy ORM models
│   ├── schemas.py          ← Pydantic request/response models
│   ├── database.py         ← SQLAlchemy engine + session factory
│   ├── tasks.py            ← Celery tasks + Beat schedule
│   ├── seed.py             ← one-time hero data seeder
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── railway.toml        ← Railway deployment config
│   ├── alembic/            ← database migration files
│   ├── routers/
│   │   ├── leaderboard.py  ← GET /api/v1/leaderboard/{region}
│   │   ├── players.py      ← GET /api/v1/players/{name}
│   │   ├── heroes.py       ← GET /api/v1/heroes/
│   │   └── websocket.py    ← WS /ws/leaderboard/{region}
│   ├── services/
│   │   ├── cache.py            ← async Redis client + get/set helpers
│   │   ├── deadlock_client.py  ← httpx client for deadlock-api.com
│   │   ├── leaderboard.py      ← Redis sorted set read/write
│   │   ├── response_cache.py   ← HTTP response cache decorator
│   │   ├── connection_manager.py ← WebSocket connection registry
│   │   └── pubsub_listener.py  ← Redis pub/sub → WebSocket bridge
│   └── tests/
│       └── test_deadlock_client.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LeaderboardTable.tsx
│   │   │   ├── RankBadge.tsx
│   │   │   ├── HeroIcons.tsx
│   │   │   ├── RegionSelector.tsx
│   │   │   ├── ConnectionStatus.tsx
│   │   │   ├── RankHistoryChart.tsx
│   │   │   ├── SkeletonRow.tsx
│   │   │   └── NavBar.tsx
│   │   ├── hooks/
│   │   │   ├── useLeaderboard.ts
│   │   │   ├── usePlayer.ts
│   │   │   └── useLeaderboardSocket.ts
│   │   ├── lib/
│   │   │   └── api.ts          ← all fetch calls in one place
│   │   ├── pages/
│   │   │   ├── LeaderboardPage.tsx
│   │   │   └── PlayerPage.tsx
│   │   ├── types/
│   │   │   └── api.ts          ← TypeScript interfaces for API responses
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── vite.config.ts
│   └── package.json
├── docker-compose.yml
├── .env.example
└── .pre-commit-config.yaml
```

---

## Local setup

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — runs Postgres, Redis, API, and workers
- [Node.js 20+](https://nodejs.org/) — for the React frontend
- Git

### 1. Clone and configure

```bash
git clone https://github.com/yourusername/statTrack
cd statTrack

# create your local environment file
cp .env.example .env
# the defaults work out of the box — no changes needed for local dev
```

### 2. Start the backend

```bash
# build and start all 5 containers: api, worker, beat, postgres, redis
docker compose up --build
```

Leave this running. Open a second terminal for the next steps.

```bash
# run database migrations — creates all tables
docker compose exec api alembic upgrade head

# seed the heroes table from deadlock-api.com
docker compose exec api python seed.py
```

The backend is now running:

| Service | URL |
|---|---|
| FastAPI | http://localhost:8000 |
| Interactive API docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |
| Prometheus metrics | http://localhost:8000/metrics |
| Flower (Celery monitor) | http://localhost:5555 |

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the leaderboard loads automatically.

The first Celery Beat cycle fires 5 minutes after startup. To populate data immediately without waiting:

```bash
docker compose exec worker celery -A tasks call tasks.refresh_leaderboard --args='["NAmerica"]'
docker compose exec worker celery -A tasks call tasks.refresh_leaderboard --args='["Europe"]'
docker compose exec worker celery -A tasks call tasks.refresh_leaderboard --args='["Asia"]'
```

---

## Environment variables

### Backend (`.env` / Railway)

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://deadlock:deadlock@postgres:5432/deadlock` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) | `https://your-app.vercel.app` |
| `SENTRY_DSN` | Sentry error tracking DSN | `https://xxx@sentry.io/xxx` |
| `ENVIRONMENT` | Deployment environment label | `production` |
| `RAILWAY_API_URL` | Public Railway URL for keepalive ping | `https://api.railway.app` |

### Frontend (Vercel)

| Variable | Description | Example |
|---|---|---|
| `VITE_API_URL` | Backend base URL | `https://your-api.railway.app` |
| `VITE_WS_URL` | WebSocket base URL | `wss://your-api.railway.app` |
| `VITE_SENTRY_DSN` | Sentry DSN for frontend errors | `https://xxx@sentry.io/xxx` |

---

## API reference

### REST endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/api/v1/leaderboard/{region}` | Ranked leaderboard for a region |
| `GET` | `/api/v1/leaderboard/{region}/player/{name}` | A player's rank in a region |
| `GET` | `/api/v1/players/{name}` | Player profile with ranks across all regions |
| `GET` | `/api/v1/players/{name}/history` | Rank history over time |
| `GET` | `/api/v1/heroes/` | All playable heroes |
| `GET` | `/api/v1/heroes/{id}` | Single hero by ID |

**Valid regions:** `NAmerica` `Europe` `Asia` `SAmerica` `Oceania`

**Leaderboard query params:**
- `limit` — number of results (1–100, default 50)
- `offset` — pagination offset (default 0)

**Example:**
```bash
curl "https://your-api.railway.app/api/v1/leaderboard/NAmerica?limit=10&offset=0"
```

### WebSocket

```
ws://localhost:8000/ws/leaderboard/{region}
```

**Messages from server:**

```json
// sent immediately on connect — current top 20
{ "event": "snapshot", "region": "NAmerica", "total": 1002, "entries": [...] }

// sent after every Celery refresh
{ "event": "leaderboard_updated", "region": "NAmerica", "updated": 1002 }

// sent every 30s to keep connection alive
{ "event": "ping" }
```

---

## Database schema

```
heroes
  id, name, class_name, hero_type, icon_url

players
  account_name (PK), account_id (nullable), first_seen, last_seen

leaderboard_snapshots
  id, account_name (FK), region, rank, badge_level,
  ranked_rank, ranked_subrank, top_hero_ids, snapshot_at

player_hero_stats
  id, account_name (FK), hero_id (FK), matches_played,
  wins, kills, deaths, assists, last_updated

mmr_history
  id, account_name (FK), mmr, recorded_at
```

`leaderboard_snapshots` is the most important table. Every Celery run inserts one row per player — this accumulates rank history over time, enabling the trend graph on player profiles. Rows older than 30 days are deleted automatically by the nightly cleanup task.

---

## Redis key patterns

| Key pattern | Type | Contents | TTL |
|---|---|---|---|
| `leaderboard:{region}` | Sorted set | member=account_name, score=badge_level | 10 min |
| `leaderboard:meta:{region}:{name}` | String | JSON blob with rank/hero metadata | 6 min |
| `cache:leaderboard:{hash}` | String | Serialized HTTP response | 30 sec |
| `cache:heroes:{hash}` | String | Serialized heroes response | 1 hour |
| `api:leaderboard:{region}` | String | Raw API response cache | 5 min |

---

## Running tests

```bash
# run all backend tests
docker compose exec api pytest tests/ -v

# run with coverage
docker compose exec api pytest tests/ -v --cov=. --cov-report=term-missing

# run frontend type check
cd frontend && npx tsc --noEmit

# run frontend linter
cd frontend && npm run lint
```

---

## Celery tasks

| Task | Schedule | Description |
|---|---|---|
| `refresh_leaderboard` | Every 5 min (staggered) | Fetches leaderboard from API → writes to Postgres + Redis |
| `cleanup_old_snapshots` | Daily | Deletes leaderboard snapshots older than 30 days |
| `keepalive_ping` | Every 25 min | Pings `/health` to prevent Railway free tier suspension |

Staggered start times prevent concurrent tasks from causing deadlocks on shared player rows:
- NAmerica → fires immediately
- Europe → offset 100 seconds
- Asia → offset 200 seconds

Manually trigger a task:

```bash
docker compose exec worker celery -A tasks call tasks.refresh_leaderboard --args='["NAmerica"]'
```

Monitor task status via Flower at http://localhost:5555.

---

## CI/CD pipeline

```
Every push to any branch:
  → run pytest (backend)
  → run TypeScript check + ESLint (frontend)
  → build Docker image (verifies Dockerfile)

Merge to main:
  → all of the above, plus:
  → build Docker image → push to GitHub Container Registry
  → trigger Railway redeploy via webhook
  → wait 30s → hit /health → confirm 200
```

Required GitHub secrets:

| Secret | Where to get it |
|---|---|
| `RAILWAY_DEPLOY_WEBHOOK` | Railway → service → Settings → Deploy Webhook |
| `RAILWAY_API_URL` | Railway → service → Settings → Domains |

---

## Deployment

### Railway (backend)

1. Create a new Railway project
2. Add PostgreSQL and Redis plugins
3. Create three services from this repo pointing to `backend/`:
   - **api** — `alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **worker** — `celery -A tasks worker --loglevel=info`
   - **beat** — `celery -A tasks beat --loglevel=info` (keep at exactly 1 replica)
4. Set environment variables on each service (see table above)
5. Run migrations and seed heroes once:
   ```bash
   railway run alembic upgrade head
   railway run python seed.py
   ```

### Vercel (frontend)

1. Import repo on vercel.com
2. Set root directory to `frontend/`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Set `VITE_API_URL` and `VITE_WS_URL` environment variables

After both are deployed, push to `main` — GitHub Actions handles every deploy automatically from that point forward.

---

## Known limitations

- `possible_account_ids` from the deadlock API is unreliable — many top players have empty arrays (privacy setting) and some IDs appear for multiple player names. `account_name` is used as the primary identifier throughout.
- MMR history and hero stats endpoints require an unambiguous `account_id` — only ~30–40% of leaderboard players expose this.
- Railway free tier suspends after 30 min of inactivity. The keepalive task prevents this, but cold starts still occur if the keepalive itself fails. Upgrade to Hobby ($5/month) to eliminate this entirely.
- The leaderboard is eventually consistent — there is up to a 30-second window where the HTTP response cache may return data that is one Celery cycle old. WebSocket clients always receive a notification within seconds of fresh data arriving.

---

## Concepts learned

Building this project covers the following system design and engineering concepts:

| Concept | Day | Implementation |
|---|---|---|
| Horizontal scaling | 1 | Separate API and worker containers |
| DB normalization | 2 | Heroes/players/snapshots schema design |
| Rate limiting | 3 | httpx client with tenacity backoff |
| Task queues + idempotency | 4 | Celery with upsert writes |
| Data structure selection | 5 | Redis sorted sets vs Postgres ORDER BY |
| CQRS | 6 | Write path (Celery) separate from read path (FastAPI) |
| Cache invalidation | 7 | TTL + event-driven invalidation hybrid |
| Pub/Sub messaging | 8 | Redis channels → WebSocket broadcast |
| Client state management | 9 | TanStack Query for server state |
| UI virtualization | 10 | Skeleton loading, pagination |
| Optimistic updates | 11 | WebSocket events → React Query cache |
| CI/CD | 12 | GitHub Actions test + deploy pipeline |
| 12-factor app | 13 | Config via env vars, stateless processes |
| SRE golden signals | 14 | Latency, traffic, errors, saturation via Prometheus |
