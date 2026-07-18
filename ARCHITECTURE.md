# Architecture

> Target architecture for this project (work in progress).

**Verified RAG Assistant** — a retrieval-augmented generation (RAG) API over a
document corpus, served with FastAPI. Every answer is grounded in the retrieved
context and cited back to its source; when the answer isn't in the corpus, the
assistant says so. Built to be *measured*: shipped with a retrieval + answer-
faithfulness evaluation report.

## Request flow

```
Client (React UI) ──HTTP──▶ FastAPI  /ask ──▶ RagService
                                                 ├─ retriever  →  Chroma vector store
                                                 └─ LLM (grounded prompt)  →  answer + sources
```

The vector index is built **once, offline** by a build script and persisted to
disk. The API loads it at startup and only *reads* from it — building and serving
are deliberately separate concerns.

## Project structure

```
src/
  app/                 # importable package (installed editable via uv)
    main.py            # create_app() factory: FastAPI, CORS, mount routers, GET /health
    config.py          # typed settings (pydantic-settings), loaded from environment
    logging_config.py  # structured logging setup
    rag/               # the RAG feature module
      router.py        # HTTP layer — thin; defines POST /ask
      schemas.py       # request/response models (pydantic)
      service.py       # business logic — retrieval + grounded generation
scripts/
  build_index.py       # one-off: load → split → embed → persist the vector store
tests/
  conftest.py          # shared fixtures (FastAPI TestClient)
  test_health.py
frontend/              # React (Vite) chat UI — added after the API
pyproject.toml         # dependencies + packaging (src layout)
Dockerfile
```

## Design conventions

- **Feature-module layout.** Each feature is a folder with a fixed trio —
  `router.py` (HTTP), `schemas.py` (I/O models), `service.py` (logic). Scales
  cleanly as features are added.
- **Thin routers, fat services.** Route handlers validate input and delegate;
  all RAG/LLM logic lives in the service layer, unit-testable in isolation.
- **Centralized, typed config.** A single `Settings` object reads from the
  environment / `.env`. No scattered `os.getenv`. Secrets are never committed.
- **Dependency injection.** Services are provided to routes via FastAPI
  `Depends`, so tests can substitute fakes.
- **App factory.** `create_app()` returns a configured `FastAPI`, keeping import
  side effects out and making test setup trivial.
- **Build / serve split.** Index building (expensive) is separate from serving
  (read-only). A fresh clone runs `build_index.py` once before serving.
- **`src/` layout.** Application code lives under `src/app/` and is installed as
  an editable package, so imports (`from app...`) resolve identically in the app,
  scripts, and tests — and the package can't be imported by accident from the
  repo root.

## Tech stack

| Concern            | Choice                                             |
| ------------------ | -------------------------------------------------- |
| API                | FastAPI + Uvicorn                                  |
| RAG framework      | LangChain                                          |
| Vector store       | Chroma (local, persisted)                          |
| Embeddings + LLM   | Azure OpenAI (provider-swappable — see README)     |
| Config             | pydantic-settings                                  |
| Frontend           | React (Vite)                                       |
| Tooling            | uv, Ruff, pytest                                   |
| Evaluation         | LangSmith (retrieval hit-rate + answer faithfulness) |

## Running

```bash
uv sync                                   # install dependencies
uv run python scripts/build_index.py      # build the vector index (once)
uv run uvicorn app.main:app --reload      # serve the API — interactive docs at /docs
```
