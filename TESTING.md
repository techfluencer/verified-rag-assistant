# Testing / Smoke Checks

Quick manual checks used while building each component. Run from the repo root.
Automated `pytest` tests live in `tests/`; these are fast sanity checks.

**Prereqs:** `uv sync`, a populated `.env`, and the vector index built once:
```bash
uv run python scripts/build_index.py
```

---

## Package import (src layout)
```bash
uv run python -c "import app; print(app.__file__)"
```
Expect a path ending in `src/app/__init__.py` (confirms the editable install).

## `app/config.py` — settings load from `.env`
```bash
uv run python -c "from app.config import settings; print(settings.azure_openai_chat_deployment, settings.persist_dir)"
```
Expect: `gpt-4o-mini <...>/chroma_db`.

## `scripts/build_index.py` — build the vector store
```bash
uv run python scripts/build_index.py
```
Expect: `12 docs -> 380 chunks`, then `Persisted 380 vectors ...`.

## `app/rag/service.py` — grounded answers + sources
In-scope (should answer + cite):
```bash
uv run python -c "from app.rag.service import RagService; import json; print(json.dumps(RagService().ask('which text splitter is recommended?'), indent=2))"
```
Expect: an answer naming `RecursiveCharacterTextSplitter` + a `sources` list.

Out-of-scope (faithfulness check — should refuse):
```bash
uv run python -c "from app.rag.service import RagService; import json; print(json.dumps(RagService().ask('what is the capital of France?'), indent=2))"
```
Expect: `"answer": "I don't know."` and `"sources": []`.

## `app/rag/schemas.py` — request/response models
```bash
uv run python -c "from app.rag.schemas import AskRequest, AskResponse; print(AskRequest(question='hi')); print(AskResponse(answer='x'))"
```
Expect both objects to print; `sources=[]` by default.

## `app/rag/router.py` — route registered
```bash
uv run python -c "from app.rag.router import router; print([(r.methods, r.path) for r in router.routes])"
```
Expect: `[({'POST'}, '/rag/ask')]`.

## `app/main.py` — run the API
```bash
uv run uvicorn app.main:app --reload
```
Then open <http://localhost:8000/docs> and try:
- `GET /health` → `{"status": "ok"}`
- `POST /rag/ask` with `{"question": "which text splitter is recommended?"}`
  (the first call is slow — the RagService lazy-loads the vector store + model clients).
