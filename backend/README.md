# ComptaRAG backend

FastAPI app for [ComptaRAG](../README.md), an agentic RAG assistant for accounting and financial-law questions. This document covers the backend specifically, for the project overview, frontend, and Firebase setup, see the [root README](../README.md).

## Table of contents

1. [Stack](#1-stack)
2. [Getting started](#2-getting-started)
3. [Project structure](#3-project-structure)
4. [The RAG pipeline](#4-the-rag-pipeline)
5. [Roles and authorization](#5-roles-and-authorization)
6. [Building the knowledge base](#6-building-the-knowledge-base)
7. [Testing](#7-testing)

## 1. Stack

FastAPI on Python 3.12, with a [LangGraph](https://github.com/langchain-ai/langgraph) agent orchestrating retrieval and generation. ChromaDB stores the vector index locally, embeddings run through Ollama, generation runs through Gemini, and Tavily provides a web-search fallback. Firebase Admin SDK verifies the ID tokens the frontend sends and reads/writes the Firestore collections described in the [root README's data model section](../README.md#6-data-model-and-stats). Tests run on pytest, with ruff for linting and mypy for type checking.

## 2. Getting started

From `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
.venv\Scripts\activate        # Windows

pip install -e ".[dev]"
```

`.[dev]` pulls in pytest, ruff, and mypy alongside the runtime dependencies, see [section 7](#7-testing) for running them. The `.env` file, Ollama setup, and `uvicorn main:app --reload` command are covered in the [root README's getting started section](../README.md#41-backend), and a template for the required environment variables lives at `.env.example`.

## 3. Project structure

```
backend/
  main.py            FastAPI app: CORS, router registration, startup hooks.
  config/            Environment variables, Firebase init, LLM client, prompts.
  core/               Cross-cutting logic: auth (core/security.py), chats (core/chats.py), stats (core/stats.py).
  routes/            HTTP layer: auth.py, admin.py, chats.py. Thin, delegate to core/ and graph/.
  graph/             The LangGraph agent: state.py defines the shared state, nodes/ holds each step.
  services/          Thin clients for external systems: chroma_service.py, search_service.py.
  models/            Shared enums and types, currently just roles.py.
  knowledge_base/    Scripts that build the local ChromaDB index (not run at request time).
  tests/             unit/ tests core/graph/services logic in isolation, integration/ exercises routes through a TestClient with a fake Firestore.
```

Everything under `config/`, `core/`, `graph/`, `routes/`, and `services/` is imported directly, `backend/` is the working directory the app runs from (`uvicorn main:app` from inside `backend/`), it is not installed as a package.

## 4. The RAG pipeline

`graph/workflow.py` wires five nodes into a `StateGraph`, one call to `POST /chats/{id}/messages` runs the whole graph once:

1. **Router** (`graph/nodes/router.py`): asks the LLM to classify the query into a category (used both to pick a ChromaDB partition and to decide the next node).
2. **Retrieve** (`graph/nodes/retrieve.py`): embeds the query with Ollama and queries ChromaDB, filtered to the router's category, for the 5 closest chunks. Skipped when the router already classified the query as `general_knowledge`.
3. **Validate** (`graph/nodes/validate.py`): asks the LLM whether the retrieved context actually answers the query. `general_knowledge` queries skip this and are always considered valid.
4. **Web search** (`graph/nodes/web_search.py`): runs only when validation fails, calls Tavily as a fallback source of context.
5. **Generate** (`graph/nodes/generate.py`): produces the final answer with Gemini, grounded in whichever context is available and the last 10 turns of conversation history, and reports token usage back to the caller.

The shared state (`graph/state.py`) is a `TypedDict` carrying the query, conversation history, category, context, answer, validation flag, and token usage between nodes. `routes/chats.py` invokes the compiled graph (`graph.workflow.app`) with the query and recent history, then persists both the user's message and the assistant's reply.

## 5. Roles and authorization

`core/security.py` verifies the Firebase ID token on every request and fetches (or creates, on first sign-in) the caller's Firestore profile, this is what `Depends(get_current_user)` resolves to in every route. `require_roles(*roles)` builds a dependency that raises 403 unless the caller's role is in the given set, used throughout `routes/admin.py`. `models/roles.py` defines the three roles and their ordering. The [root README's roles section](../README.md#5-authentication-and-roles) covers what each role can do from a product point of view, `routes/admin.py` is the enforcement layer: `ADMIN` can delete `USER` accounts and promote/demote between `USER` and `ADMIN`, `SUPER_ADMIN` can additionally delete `ADMIN` accounts and assign any role. Neither can touch the `SUPER_ADMIN` account or their own account.

## 6. Building the knowledge base

`knowledge_base/` is a one-time (or whenever source documents change) pipeline, not something the running app calls:

- `extract_text.py` pulls text out of source PDFs with `pypdf`.
- `preprocess.py` cleans the extracted text (collapsing whitespace, stripping stray characters).
- `create_db.py` chunks the cleaned text, embeds each chunk through Ollama, and writes it into the local ChromaDB collection at `knowledge_base/chroma_db`, which `services/chroma_service.py` reads from at request time.

Run `python knowledge_base/create_db.py` from `backend/` after adding or changing source documents, see the [root README's getting started section](../README.md#41-backend) for the full one-time setup.

## 7. Testing

From `backend/`, with the `dev` extra installed:

```bash
pytest        # runs unit/ and integration/, with coverage (see pytest.ini)
ruff check .
mypy .
```

`tests/unit/` covers `core/`, `graph/nodes/`, and `services/` in isolation, mocking their external dependencies (Firestore, Ollama, Gemini, Tavily). `tests/integration/` exercises the actual FastAPI routes through a `TestClient`, with `get_current_user` overridden to a fixed caller and Firestore replaced by the in-memory fake at `tests/setup/fakes.py`, so no test ever needs real Firebase credentials or a running Ollama instance. All three checks run in CI on every push and pull request to `main`, see `.github/workflows/ci.yml`.