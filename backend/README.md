# ComptaRAG backend

FastAPI app for [ComptaRAG](../README.md), an agentic RAG assistant for accounting and financial-law questions. This document covers the backend specifically, for the project overview and frontend, see the [root README](../README.md).

## Table of contents

1. [Stack](#1-stack)
2. [Getting started](#2-getting-started)
3. [Project structure](#3-project-structure)
4. [The RAG pipeline](#4-the-rag-pipeline)
5. [Roles and authorization](#5-roles-and-authorization)
6. [Data model](#6-data-model)
7. [Rate limiting](#7-rate-limiting)
8. [Building the knowledge base](#8-building-the-knowledge-base)
9. [Testing](#9-testing)

## 1. Stack

FastAPI on Python 3.12, with a [LangGraph](https://github.com/langchain-ai/langgraph) agent orchestrating retrieval and generation. ChromaDB stores the vector index locally, embeddings run through Ollama, generation runs through Gemini, and Tavily provides a web-search fallback. Firebase Admin SDK verifies the ID tokens the frontend sends and reads/writes the Firestore collections described in [section 6](#6-data-model). [slowapi](https://github.com/laurentS/slowapi) rate limits every route, see [section 7](#7-rate-limiting). Tests run on pytest, with ruff for linting and mypy for type checking.

## 2. Getting started

From `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
.venv\Scripts\activate        # Windows

pip install -e ".[dev]"
```

`.[dev]` pulls in pytest, ruff, and mypy alongside the runtime dependencies, see [section 9](#9-testing) for running them.

Create a `.env` file in `backend/` (a template lives at `.env.example`):

```
GEMINI_API_KEY=<your-key>
TAVILY_API_KEY=<your-key>
FIREBASE_PROJECT_ID=<your-firebase-project-id>
FIREBASE_SERVICE_ACCOUNT_PATH=<path-to-your-service-account.json>
```

`FIREBASE_PROJECT_ID` and `FIREBASE_SERVICE_ACCOUNT_PATH` come from the Firebase project set up below. An optional `FRONTEND_ORIGIN` variable controls which origin is allowed to call the API (CORS), it defaults to `http://localhost:4200`. `.env.example` also lists the rate-limiting env vars covered in [section 7](#7-rate-limiting).

You also need [Ollama](https://ollama.com/download) running locally with the embedding model pulled:

```bash
ollama pull embeddinggemma
```

### Firebase setup

Authentication runs on Firebase, both this backend and the [frontend](../frontend/README.md) need to point at the same Firebase project.

1. Create a project at [console.firebase.google.com](https://console.firebase.google.com), if you do not already have one.
2. Under **Build > Authentication > Sign-in method**, enable the **Email/Password** and **Google** providers.
3. Under **Build > Firestore Database**, create a database. The app manages the `users`, `chats`, `login_events`, and `usage_totals` collections itself, no manual setup is needed there, but you should still set security rules that block direct client reads and writes to all of them, since all access goes through this backend. Then deploy the composite index the chat list needs, `firebase deploy --only firestore:indexes` from the repo root (needs the [Firebase CLI](https://firebase.google.com/docs/cli), logged into this project), see [section 6](#6-data-model) for why it is needed.
4. Under **Project settings > Service accounts**, generate a new private key. This downloads a JSON file, save it somewhere on disk and point `FIREBASE_SERVICE_ACCOUNT_PATH` at it in `.env`. Set `FIREBASE_PROJECT_ID` to the project ID shown at the top of that same page. This file is a credential, keep it out of version control.
5. Under **Project settings > General > Your apps**, add a web app if you do not have one, and copy its config object into `frontend/src/environments/environment.ts` and `environment.prod.ts` (see the [frontend README's getting started section](../frontend/README.md#2-getting-started)). This config is public client identification, not a secret, it is safe to commit once filled in.
6. The very first account anyone creates, through either sign-in method, automatically becomes `SUPER_ADMIN`. Every account after that starts as `USER`. Sign up first to claim that role, then use the admin page at `/admin/users` to promote others.

Build the local knowledge base (one-time, or whenever the source documents change):

```bash
python knowledge_base/create_db.py
```

Run the API:

```bash
uvicorn main:app --reload
```

The API comes up at `http://127.0.0.1:8000`. Chats live under `/chats`: `POST /chats/` starts a new chat, `GET /chats/` lists yours, `GET /chats/{id}` returns one with its full message history, `PATCH /chats/{id}` renames it, `DELETE /chats/{id}` removes it, and `POST /chats/{id}/messages` sends a message, the agent answers with the chat's last 10 messages as conversational context, and both messages are saved.

## 3. Project structure

```
backend/
  main.py            FastAPI app: CORS, rate limiter wiring, router registration, startup hooks.
  config/            Environment variables, Firebase init, LLM client, prompts.
  core/              Cross-cutting logic: auth (core/security.py), rate limiting (core/rate_limit.py), logging (core/logger.py).
  routes/            HTTP layer: auth.py, admin.py, chats.py. Thin, delegate to core/, services/, and graph/.
  graph/             The LangGraph agent: state.py defines the shared state, nodes/ holds each step.
  services/          Business logic and thin clients for external systems: chats_service.py, users_service.py, stats_service.py, limits_service.py, chroma_service.py, search_service.py.
  schemas/           Pydantic request/response models and shared enums, including roles.py.
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
5. **Generate** (`graph/nodes/generate.py`): produces the final answer with Gemini, grounded in whichever context is available and the last 10 turns of conversation history, and reports token usage back to the caller. If the provider call returns no text (for example, both configured LLM providers are exhausted), it returns a fixed apology message with zeroed token usage instead of an empty reply.

The shared state (`graph/state.py`) is a `TypedDict` carrying the query, conversation history, category, context, answer, validation flag, and token usage between nodes. `routes/chats.py` invokes the compiled graph (`graph.workflow.app`) with the query and recent history, then persists both the user's message and the assistant's reply.

## 5. Roles and authorization

Every page requires a signed-in user, except the public landing page at `/`, which shows sign-in and sign-up options to visitors and redirects anyone already signed in straight to `/chat`. There are three roles:

- `USER`: can use the chat. This is the default role for every new account after the first.
- `ADMIN`: everything `USER` can do, plus access to `/admin/users`, where they can promote or demote accounts between `USER` and `ADMIN`. An `ADMIN` cannot modify a `SUPER_ADMIN` account, and cannot grant the `SUPER_ADMIN` role to anyone.
- `SUPER_ADMIN`: everything `ADMIN` can do, plus the ability to assign any role, including `SUPER_ADMIN`, to any account. The very first account ever created gets this role automatically, so there is always at least one admin able to promote everyone else.

Nobody can change their own role, to avoid accidentally locking themselves out.

`core/security.py` verifies the Firebase ID token on every request and fetches (or creates, on first sign-in) the caller's Firestore profile, this is what `Depends(get_current_user)` resolves to in every route. `require_roles(*roles)` builds a dependency that raises 403 unless the caller's role is in the given set, used throughout `routes/admin.py`, which is the enforcement layer for the rules above: `ADMIN` can delete `USER` accounts and promote/demote between `USER` and `ADMIN`, `SUPER_ADMIN` can additionally delete `ADMIN` accounts and assign any role. Neither can touch the `SUPER_ADMIN` account or their own account. `schemas/roles.py` defines the three roles and their ordering.

On the frontend, `core/guards/auth.guard.ts` blocks unauthenticated visitors from `/chat` and sends signed-in visitors away from the public landing page and login screen, and `core/guards/role.guard.ts` restricts `/admin/users` to `ADMIN` and `SUPER_ADMIN`, both mirror the rules above so the UI never offers an action the API would reject, but this backend remains the source of truth. See the [frontend README](../frontend/README.md) for how those guards fit into routing.

## 6. Data model

Everything lives in Firestore, alongside the `users` collection described above:

- `chats/{chatId}`: `owner_uid`, `title` (auto-generated from the first message, up to 60 characters), `created_at`, `updated_at`. Only the owner can read, rename, or delete a chat.
- `chats/{chatId}/messages/{messageId}`: `role` (`user` or `assistant`), `content`, `created_at`, and on assistant messages, `category` (the router's classification) and `token_usage`. The last 10 messages of a chat are passed to the agent as conversation history on every new message.
- `login_events/{eventId}`: `uid`, `email`, `ip`, `user_agent`, `created_at`, one entry per call to `GET /auth/me`, which the frontend calls right after every sign-in. Each user's profile also gets a `last_login_at` / `last_login_ip` stamp for a quick per-user summary without scanning events.
- `usage_totals/{uid}`: `prompt_tokens`, `completion_tokens`, `total_tokens`, `message_count`, a running total updated after every assistant reply, so reading usage stats does not require summing every message ever sent.

`GET /admin/stats/logins` and `GET /admin/stats/usage` (both `ADMIN`/`SUPER_ADMIN` only) expose this data for an admin dashboard. See the [frontend README](../frontend/README.md) for how the chat page and admin dashboard consume these endpoints.

Listing a user's chats filters on `owner_uid` and orders by `updated_at`, Firestore needs a composite index for that combination. It is declared in `firestore.indexes.json` at the repo root, deploy it once per project with `firebase deploy --only firestore:indexes` (needs the [Firebase CLI](https://firebase.google.com/docs/cli), logged into the same project, see [section 2](#2-getting-started)). Skipping this makes `GET /chats/` fail with a `FAILED_PRECONDITION` error the first time it runs, the error itself includes a direct "create this index" link as a fallback.

## 7. Rate limiting

Every route is rate limited with [slowapi](https://github.com/laurentS/slowapi), configured in `core/rate_limit.py` and wired into `main.py`. Limits are keyed by the caller's IP address, honoring `X-Forwarded-For` behind a proxy or load balancer via the same helper `services/stats_service.py` uses for login logging, so limits apply per client regardless of authentication state.

A global default limit applies automatically to any route without a more specific one, and `routes/auth.py`, `routes/chats.py`, and `routes/admin.py` each override it where a tighter or looser limit fits better. `POST /chats/{id}/messages`, which triggers the full RAG/LLM pipeline, gets the strictest limit. All limits are configurable through environment variables, shown here with their defaults:

| Env var | Default | Applies to |
| --- | --- | --- |
| `RATE_LIMIT_ENABLED` | `true` | Turns the whole limiter on or off. |
| `DEFAULT_RATE_LIMIT` | `100/minute` | Any route without a more specific limit. |
| `AUTH_RATE_LIMIT` | `30/minute` | `GET`/`PATCH /auth/me`. |
| `CHAT_RATE_LIMIT` | `60/minute` | Chat CRUD, `POST`/`GET`/`PATCH`/`DELETE /chats*`. |
| `CHAT_MESSAGE_RATE_LIMIT` | `20/minute` | `POST /chats/{id}/messages`. |
| `ADMIN_RATE_LIMIT` | `60/minute` | Every route in `routes/admin.py`. |

A caller that exceeds a limit gets a `429` with a JSON body naming the limit that was hit. This sits alongside, and is stricter than, the daily/monthly token and search quotas in `services/limits_service.py` (see [section 4](#4-the-rag-pipeline)): that system caps how much of the LLM/Tavily budget a user can consume overall, this one caps how fast any single caller can hit the API in the first place.

Sign-up and sign-in themselves are not backend routes, the frontend talks to Firebase Authentication directly (see [section 5](#5-roles-and-authorization)), so those two flows are protected by Firebase's own abuse controls rather than anything in this repository. `GET`/`PATCH /auth/me`, called right after every sign-in and on every profile edit, is the closest equivalent surface we own, and is rate limited accordingly.

Tests live in `tests/unit/core/test_rate_limit.py` (the key function and the enable/disable env var) and `tests/integration/test_rate_limit.py` (the slowapi wiring end to end, including 429s and independent per-IP buckets). The rest of the suite runs with `RATE_LIMIT_ENABLED=false` (set in `tests/setup/mock_modules.py`), since it exercises the same handful of real routes hundreds of times and should not depend on call order or count.

## 8. Building the knowledge base

`knowledge_base/` is a one-time (or whenever source documents change) pipeline, not something the running app calls:

- `extract_text.py` pulls text out of source PDFs with `pypdf`.
- `preprocess.py` cleans the extracted text (collapsing whitespace, stripping stray characters).
- `create_db.py` chunks the cleaned text, embeds each chunk through Ollama, and writes it into the local ChromaDB collection at `knowledge_base/chroma_db`, which `services/chroma_service.py` reads from at request time.

Run `python knowledge_base/create_db.py` from `backend/` after adding or changing source documents, see [section 2](#2-getting-started) for the full one-time setup.

## 9. Testing

From `backend/`, with the `dev` extra installed:

```bash
pytest        # runs unit/ and integration/, with coverage (see pytest.ini)
ruff check .
mypy .
```

`tests/unit/` covers `core/`, `graph/nodes/`, and `services/` in isolation, mocking their external dependencies (Firestore, Ollama, Gemini, Tavily). `tests/integration/` exercises the actual FastAPI routes through a `TestClient`, with `get_current_user` overridden to a fixed caller and Firestore replaced by the in-memory fake at `tests/setup/fakes.py`, so no test ever needs real Firebase credentials or a running Ollama instance. All three checks run in CI on every push and pull request to `main`, see `.github/workflows/ci.yml`.