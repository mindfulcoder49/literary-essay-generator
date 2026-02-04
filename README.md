# Literary Essays MVP

FastAPI + worker MVP that ingests Project Gutenberg books, indexes paragraphs in Pinecone Serverless, and generates theme-based essays with citations.

## Requirements

- Python 3.11+
- Postgres or SQLite
- Pinecone Serverless index
- OpenAI API key

## Quick Start (Local)

1. Create a virtualenv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure env vars:

```bash
cp .env.example .env
```

3. Run migrations (from repo root):

```bash
alembic upgrade head
```

If you are using SQLite, a `literary.db` file will be created.

If you run from `app/`, use:

```bash
alembic -c alembic.ini upgrade head
```

If you already ran migrations, run the latest:

```bash
alembic upgrade head
```

4. Start API:

```bash
uvicorn app.main:app --reload
```

5. Start worker (separate terminal):

```bash
python -m app.worker
```

## API

- `GET /gutenberg/search?q=...`
- `POST /jobs` body `{ "gutenberg_id": 1342 }`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/result`

## Notes

- Pinecone namespace is per document: `gb:<gutenberg_id>:<hash>`.
- Evidence is retrieved by theme query embeddings; essay cites `segment_id` references.

## Logs

- API log: `app/logs/api.log`
- Worker log: `app/logs/worker.log`

## Deploy (Fly.io)

For full deployment instructions, see [DEPLOY.md](./DEPLOY.md).
