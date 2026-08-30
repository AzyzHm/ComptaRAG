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
  🚧 This project is under active development. Expect breaking changes and evolving documentation until a first stable tag is cut.
</p>

---

## Table of contents

1. [What ComptaRAG does](#1-what-comptarag-does)
2. [Architecture](#2-architecture)
3. [Roadmap](#3-roadmap)
4. [Getting started](#4-getting-started)
5. [Testing](#5-testing)
6. [Contributing](#6-contributing)
7. [Security](#7-security)
8. [License](#8-license)

## 1. What ComptaRAG does

ComptaRAG is an agentic RAG assistant for accounting and financial-law questions, aimed especially at professionals in Tunisia. It combines IFRS knowledge with Tunisian tax and accounting regulations, and grounds every answer in retrieved source material instead of relying on the model's own memory.

## 2. Architecture

The project has two parts:

- **Angular frontend** (`frontend/`): the chat interface users interact with.
- **FastAPI backend** (`backend/`): a LangGraph agent that routes each question, retrieves relevant context from a ChromaDB vector store (embedded locally via Ollama), falls back to a Tavily web search when local context is not enough, and generates the final answer with Gemini.

This is the current stack. Firebase is planned for authentication, see the roadmap below.

## 3. Roadmap

Planned, not yet built:

- Firebase authentication for the Angular frontend: sign-in and user management. Guard and interceptor scaffolding already exists in `frontend/src/app/core`, it is not wired up yet.
- Conversation history: the assistant remembering and using past turns in a session.
- Selectable retrieval mode: keyword search (BM25), semantic search, or a hybrid of both.
- Reranking: retrieved chunks reranked with `jina-reranker-v2-base` before being used as context.
- Query refinement: rewriting or clarifying the user's question before retrieval, including resolving it against conversation history.
- Iterative retrieval: if retrieved context is judged insufficient, refining the query and retrieving again (up to two passes) before falling back to a web search.

None of these are implemented yet. The current pipeline is a single pass: route, retrieve, validate, generate, with a web search fallback when validation fails.

## 4. Getting started

### Backend

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
```

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

The API comes up at `http://127.0.0.1:8000`, with the chat endpoint at `POST /chat/`.

### Frontend

From `frontend/`:

```bash
npm install
npm start
```

The app comes up at `http://localhost:4200` and expects the backend to be running.

## 5. Testing

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

## 6. Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request, and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## 7. Security

Found a serious vulnerability? Please do not open a public issue, see [SECURITY.md](SECURITY.md) for how to report it responsibly.

## 8. License

This project is licensed under the [Apache License 2.0](LICENSE).