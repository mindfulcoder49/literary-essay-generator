# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Literary Essays — a FastAPI + LangGraph web app that ingests Project Gutenberg books, indexes text segments in Pinecone (vector embeddings via OpenAI), and generates theme-based literary essays with citations. Vue 3 frontend with real-time SSE progress tracking.

Two process types: a REST API server and a background job worker.

## Commands

```bash
# Backend setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd frontend && npm install

# Run frontend dev server (proxies /api to localhost:8000)
cd frontend && npm run dev

# Run API server (dev)
uvicorn app.main:app --reload

# Run background worker (separate terminal)
python -m app.worker

# Database migrations
alembic -c app/alembic.ini upgrade head

# Create new migration
alembic -c app/alembic.ini revision --autogenerate -m "description"

# Production build (frontend → app/static/)
cd frontend && npm run build
```

No test framework or linter is currently configured.

## Architecture

### Two Entry Points

- **API server** (`app/main.py`) — FastAPI app serving REST API under `/api/*` and Vue SPA static files at `/`
- **Worker** (`app/worker.py`) — Async polling loop that claims and processes jobs via LangGraph every 3 seconds

### LangGraph Pipeline (`app/graph/`)

A `POST /api/jobs` request with a Gutenberg book ID creates a single `essay_pipeline` job. The worker runs a LangGraph state graph with 7 nodes:

1. **`ingest_node`** — Fetch Gutenberg text → normalize → segment → embed via `OpenAIEmbeddings` → upsert to Pinecone
2. **`discover_themes_node`** — LLM identifies 4-6 literary themes via `ChatOpenAI`
3. **`retrieve_evidence_node`** — Batch-embed themes → query Pinecone top-8 per theme
4. **`draft_essay_node`** — LLM generates structured essay with `[segment_id]` citations
5. **`review_essay_node`** — LLM self-critiques for theme coverage, citation accuracy, coherence
6. **`revise_essay_node`** — LLM revises based on review feedback (max 2 revisions)
7. **`persist_results_node`** — Writes `JobArtifact` rows, marks job succeeded

Graph flow: `ingest → discover_themes → retrieve_evidence → draft_essay → review_essay → (conditional: persist_results OR revise_essay → review_essay) → END`

### Key Modules

| Module | Role |
|--------|------|
| `config.py` | Pydantic Settings — all env vars and defaults |
| `models.py` | SQLAlchemy ORM: User, Document, Job, JobArtifact |
| `schemas.py` | Pydantic request/response models |
| `db.py` | Database engine and session factory |
| `queue.py` | Job state machine with `skip_locked` row claiming and progress tracking |
| `graph/state.py` | `EssayGraphState` TypedDict for LangGraph |
| `graph/nodes.py` | 7 graph node functions |
| `graph/builder.py` | Graph construction and compilation |
| `graph/prompts.py` | All LLM prompt templates |
| `pinecone_client.py` | Pinecone upsert/query wrapper |
| `gutenberg.py` | Gutenberg text fetching and Gutendex search |
| `segment.py` | Text splitting logic |

### Database

PostgreSQL via SQLAlchemy + psycopg. Four tables: `users`, `documents`, `jobs`, `job_artifacts`. Migrations in `app/migrations/versions/`.

Content deduplication uses SHA256 hashing of normalized text (`documents.canonical_hash`).

### External Services

- **OpenAI** (via `langchain-openai`) — embeddings + chat completions
- **Pinecone Serverless** — vector storage with per-document namespace isolation
- **Project Gutenberg / Gutendex** — book source

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Vue SPA (static files) |
| GET | `/api/health` | Health check |
| GET | `/api/gutenberg/search?q=` | Search books via Gutendex |
| POST | `/api/jobs` | Create essay pipeline job |
| GET | `/api/jobs/{job_id}` | Job status |
| GET | `/api/jobs/{job_id}/result` | Themes, evidence, essay |
| GET | `/api/jobs/{job_id}/stream` | SSE real-time progress |

### Frontend (Vue 3)

Vue 3 + TypeScript + Vite SPA in `frontend/`. Key structure:
- `src/api/` — fetch wrapper, gutenberg, jobs API clients
- `src/composables/useJobStream.ts` — SSE composable for real-time progress
- `src/components/` — BookSearch, JobCreator, JobProgress, ThemePills, EvidencePanel, EssayDisplay
- `src/views/` — HomeView (search + create), JobView (progress + results)
- `src/router/` — two routes: `/` and `/jobs/:id`

Dev server proxies `/api/*` to `http://localhost:8000`.

### Deployment

Docker multi-stage build (Node for frontend, Python for backend) deployed to Fly.io (`fly.toml`). Two Fly process groups: `web` (uvicorn on port 8080) and `worker` (python -m app.worker). Shared-cpu-1x, 512MB RAM.

## Environment Variables

See `.env.example`. Required: `DATABASE_URL`, `PINECONE_API_KEY`, `OPENAI_API_KEY`. The app uses `pydantic-settings` to load from environment or `.env` file.
