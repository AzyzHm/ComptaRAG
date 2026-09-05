<p align="center">
  <img src="backend/assets/ComptaRAG_banner_Image.png" alt="ComptaRAG banner" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Angular-DD0031?style=flat&logo=angular&logoColor=white" alt="Angular">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/ChromaDB-4B0082?style=flat" alt="ChromaDB">
  <img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=flat" alt="LangGraph">
  <img src="https://img.shields.io/badge/Gemini-8E75B2?style=flat&logo=googlegemini&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/Tavily-000000?style=flat" alt="Tavily">
  <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="Apache 2.0 License">
</p>

<p align="center">
 This project is under active development. Expect breaking changes and evolving documentation until a first stable tag is cut.
</p>

---

## Table of contents

1. [What ComptaRAG does](#1-what-comptarag-does)
2. [Architecture](#2-architecture)
3. [Roadmap](#3-roadmap)
4. [Getting started](#4-getting-started)
5. [Authentication and roles](#5-authentication-and-roles)
6. [Data model and stats](#6-data-model-and-stats)
7. [Testing](#7-testing)
8. [Contributing](#8-contributing)
9. [Security](#9-security)
10. [License](#10-license)

## 1. What ComptaRAG does

ComptaRAG is an agentic RAG assistant for accounting and financial-law questions, aimed especially at professionals in Tunisia. It combines IFRS knowledge with Tunisian tax and accounting regulations, and grounds every answer in retrieved source material instead of relying on the model's own memory.

## 2. Architecture

The project has two parts:

- **Angular frontend** (`frontend/`): a public landing page, sign-in/sign-up, the chat interface (with a chat history sidebar, at `/chat` and `/chat/:chatId`), and an admin page for managing user roles. The UI supports light, dark, and system themes, and the layout is responsive down to mobile, with the chat sidebar becoming an off-canvas drawer on narrow screens. See the [frontend README](frontend/README.md) for details on the theming and responsive-layout conventions.
- **FastAPI backend** (`backend/`): a LangGraph agent that routes each question, retrieves relevant context from a ChromaDB vector store (embedded locally via Ollama), falls back to a Tavily web search when local context is not enough, and generates the final answer with Gemini. See the [backend README](backend/README.md) for the pipeline's node-by-node breakdown and project structure.

Authentication is handled by Firebase: the frontend signs users in with the Firebase JS SDK (email and password, or Google), and the backend verifies the resulting ID token with the Firebase Admin SDK on every request. User profiles and roles live in a Firestore `users` collection. See [section 4.3](#43-firebase-setup) for setup, and [section 5](#5-authentication-and-roles) for how roles work.

## 3. Roadmap

Planned, not yet built:

- Selectable retrieval mode: keyword search (BM25), semantic search, or a hybrid of both.
- Reranking: retrieved chunks reranked with `jina-reranker-v2-base` before being used as context.
- Query refinement: rewriting or clarifying the user's question before retrieval, including resolving it against conversation history.
- Iterative retrieval: if retrieved context is judged insufficient, refining the query and retrieving again (up to two passes) before falling back to a web search.

None of these are implemented yet. The current pipeline is a single pass: route, retrieve, validate, generate, with a web search fallback when validation fails, and the last 10 messages of the active chat given to the generate step as conversation history.

## 4. Getting started

### 4.1 Backend

From `backend/`:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

pip install -e .
```

Create a `.env` file in `backend/` with:

```
GEMINI_API_KEY=<your-key>
TAVILY_API_KEY=<your-key>
FIREBASE_PROJECT_ID=<your-firebase-project-id>
FIREBASE_SERVICE_ACCOUNT_PATH=<path-to-your-service-account.json>
```

`FIREBASE_PROJECT_ID` and `FIREBASE_SERVICE_ACCOUNT_PATH` come from the Firebase project you set up in [section 4.3](#43-firebase-setup). An optional `FRONTEND_ORIGIN` variable controls which origin is allowed to call the API (CORS), it defaults to `http://localhost:4200`.

You also need [Ollama](https://ollama.com/download) running locally with the embedding model pulled:

```bash
ollama pull embeddinggemma
```

Build the local knowledge base (one-time, or whenever the source documents change):

```bash
python knowledge_base/create_db.py
```

Run the API:

```bash
uvicorn main:app --reload
```

The API comes up at `http://127.0.0.1:8000`. Chats live under `/chats`: `POST /chats/` starts a new chat, `GET /chats/` lists yours, `GET /chats/{id}` returns one with its full message history, `PATCH /chats/{id}` renames it, `DELETE /chats/{id}` removes it, and `POST /chats/{id}/messages` sends a message, the agent answers with the chat's last 10 messages as conversational context, and both messages are saved.

### 4.2 Frontend

From `frontend/`:

```bash
npm install
npm start
```

The app comes up at `http://localhost:4200` with a public landing page, and expects the backend to be running. Before it can sign anyone in, fill in the Firebase web config in `frontend/src/environments/environment.ts` (and `environment.prod.ts` for a production build), see [section 4.3](#43-firebase-setup).

### 4.3 Firebase setup

Authentication runs on Firebase, both the backend and the frontend need to point at the same Firebase project.

1. Create a project at [console.firebase.google.com](https://console.firebase.google.com), if you do not already have one.
2. Under **Build > Authentication > Sign-in method**, enable the **Email/Password** and **Google** providers.
3. Under **Build > Firestore Database**, create a database. The app manages the `users`, `chats`, `login_events`, and `usage_totals` collections itself, no manual setup is needed there, but you should still set security rules that block direct client reads and writes to all of them, since all access goes through the backend. Then deploy the composite index the chat list needs, `firebase deploy --only firestore:indexes` from the repo root (needs the [Firebase CLI](https://firebase.google.com/docs/cli), logged into this project), see [section 6](#6-data-model-and-stats) for why it is needed.
4. Under **Project settings > Service accounts**, generate a new private key. This downloads a JSON file, save it somewhere on disk and point `FIREBASE_SERVICE_ACCOUNT_PATH` at it in the backend's `.env`. Set `FIREBASE_PROJECT_ID` to the project ID shown at the top of that same page. This file is a credential, keep it out of version control.
5. Under **Project settings > General > Your apps**, add a web app if you do not have one, and copy its config object into `frontend/src/environments/environment.ts` and `environment.prod.ts`. This config is public client identification, not a secret, it is safe to commit once filled in.
6. The very first account anyone creates, through either sign-in method, automatically becomes `SUPER_ADMIN`. Every account after that starts as `USER`. Sign up first to claim that role, then use the admin page at `/admin/users` to promote others.

## 5. Authentication and roles

Every page requires a signed-in user, except the public landing page at `/`, which shows sign-in and sign-up options to visitors and redirects anyone already signed in straight to `/chat`. There are three roles:

- `USER`: can use the chat. This is the default role for every new account after the first.
- `ADMIN`: everything `USER` can do, plus access to `/admin/users`, where they can promote or demote accounts between `USER` and `ADMIN`. An `ADMIN` cannot modify a `SUPER_ADMIN` account, and cannot grant the `SUPER_ADMIN` role to anyone.
- `SUPER_ADMIN`: everything `ADMIN` can do, plus the ability to assign any role, including `SUPER_ADMIN`, to any account. The very first account ever created gets this role automatically, so there is always at least one admin able to promote everyone else.

Nobody can change their own role, to avoid accidentally locking themselves out.

On the backend, this is enforced by `core/security.py` (token verification and the get-or-create Firestore profile) and `routes/admin.py` (the role-change rules above). On the frontend, `core/guards/auth.guard.ts` blocks unauthenticated visitors from `/chat` and sends signed-in visitors away from the public landing page and login screen, and `core/guards/role.guard.ts` restricts `/admin/users` to `ADMIN` and `SUPER_ADMIN`, both mirror the backend's rules so the UI never offers an action the API would reject, but the backend remains the source of truth.

## 6. Data model and stats

Everything lives in Firestore, alongside the `users` collection described above:

- `chats/{chatId}`: `owner_uid`, `title` (auto-generated from the first message, up to 60 characters), `created_at`, `updated_at`. Only the owner can read, rename, or delete a chat.
- `chats/{chatId}/messages/{messageId}`: `role` (`user` or `assistant`), `content`, `created_at`, and on assistant messages, `category` (the router's classification) and `token_usage`. The last 10 messages of a chat are passed to the agent as conversation history on every new message.
- `login_events/{eventId}`: `uid`, `email`, `ip`, `user_agent`, `created_at`, one entry per call to `GET /auth/me`, which the frontend calls right after every sign-in. Each user's profile also gets a `last_login_at` / `last_login_ip` stamp for a quick per-user summary without scanning events.
- `usage_totals/{uid}`: `prompt_tokens`, `completion_tokens`, `total_tokens`, `message_count`, a running total updated after every assistant reply, so reading usage stats does not require summing every message ever sent.

The frontend's chat page (`/chat`, `/chat/:chatId`) is a two-pane layout backed directly by this data: a history sidebar backed by `GET /chats/`, and a conversation pane backed by `GET /chats/{id}` and `POST /chats/{id}/messages`. Starting a message with no chat selected creates one first, chats can be renamed or deleted from the sidebar, and the sidebar itself collapses to a thin icon rail on desktop or an off-canvas drawer on mobile.

`GET /admin/stats/logins` and `GET /admin/stats/usage` (both `ADMIN`/`SUPER_ADMIN` only) expose this data for an admin dashboard.

Listing a user's chats filters on `owner_uid` and orders by `updated_at`, Firestore needs a composite index for that combination. It is declared in `firestore.indexes.json` at the repo root, deploy it once per project with `firebase deploy --only firestore:indexes` (needs the [Firebase CLI](https://firebase.google.com/docs/cli), logged into the same project). Skipping this makes `GET /chats/` fail with a `FAILED_PRECONDITION` error the first time it runs, the error itself includes a direct "create this index" link as a fallback.

## 7. Testing

Backend, from `backend/`:

```bash
pip install -e ".[test]"
pytest
```

Frontend, from `frontend/`:

```bash
npm test
```

Both also run in CI on every push and pull request to `main`. See `.github/workflows/ci.yml` for details.

## 8. Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request, and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## 9. Security

Found a serious vulnerability? Please do not open a public issue, see [SECURITY.md](SECURITY.md) for how to report it responsibly.

## 10. License

This project is licensed under the [Apache License 2.0](LICENSE).