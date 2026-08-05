<p align="center">
  <img src="assets/ComptaRAG_banner_Image.png" alt="ComptaRAG banner" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Angular-DD0031?style=flat&logo=angular&logoColor=white" alt="Angular">
  <img src="https://img.shields.io/badge/Spring%20Boot-6DB33F?style=flat&logo=springboot&logoColor=white" alt="Spring Boot">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/RabbitMQ-FF6600?style=flat&logo=rabbitmq&logoColor=white" alt="RabbitMQ">
  <img src="https://img.shields.io/badge/Firebase-FFCA28?style=flat&logo=firebase&logoColor=black" alt="Firebase">
  <img src="https://img.shields.io/badge/ChromaDB-4B0082?style=flat" alt="ChromaDB">
  <img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=flat" alt="LangGraph">
  <img src="https://img.shields.io/badge/Gemini-8E75B2?style=flat&logo=googlegemini&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/Tavily-000000?style=flat" alt="Tavily">
  <img src="https://img.shields.io/badge/Jina%20Reranker-000000?style=flat&logo=jinja&logoColor=white" alt="Jina Reranker">
  <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="Apache 2.0 License">
</p>

<p align="center">
  🚧 <strong>Active development, this project is in a dev/pre-release phase.</strong><br>
  The architecture is currently being migrated to a multi-service design (see below). Expect breaking changes, incomplete features, and evolving documentation until a first stable tag is cut.
</p>

---

## 1. Project Objective

ComptaRAG is an agentic RAG assistant that helps people especially professionals in Tunisia get grounded answers to accounting and financial-law questions, combining IFRS knowledge with Tunisian tax and accounting regulations.

## 2. What's changing (dev phase)

The project is moving from a 2-piece app (Streamlit + FastAPI) to a proper 3-service architecture:

- **Angular frontend** : replaces Streamlit; adds authentication, an admin panel, and a richer chat experience.
- **FastAPI service** : trimmed down to just the agentic RAG pipeline (retrieval, reranking, generation).
- **Spring Boot service** : new; handles authentication and user management with three roles (super admin, admin, user), backed by Firebase (Firestore + Firebase Auth).
- **RabbitMQ** : connects the two backend services asynchronously (user lifecycle events, usage/audit logging).

Alongside the architecture change, the RAG pipeline itself is being upgraded with:

- **Conversation history** : the assistant now remembers and uses past turns in a conversation.
- **Selectable retrieval mode** : choose keyword search (BM25), semantic search, or a hybrid of both.
- **Reranking** : retrieved chunks are reranked with `jina-reranker-v2-base` before being used as context.
- **Query refinement** : the user's question is rewritten/clarified before retrieval, including resolving it against conversation history.
- **Iterative retrieval loop** : if retrieved context is judged insufficient, the assistant refines the query and retrieves again (up to two passes) before falling back to a live web search.

> Note: this README intentionally does not include code-level documentation yet , that will be added once the new architecture stabilizes. See the [Contributing](#contributing) section if you'd like to help.

## 3. Current (legacy) architecture

The diagram below reflects the *original* Streamlit + FastAPI version, kept here for reference while the migration is in progress. An updated architecture diagram will replace it once the new services are in place.

[![Architecture Diagram](assets/architecture.png)](assets/architecture.png)

## 4. Legacy Installation & Setup

These instructions apply to the current `dev` branch (pre-migration). They will change once the new services land.

```
python -m venv venv
pip install -r requirements.txt
```

For notebook/experimentation work, also install:

```
pip install -r requirements-dev.txt
```

Create a `.env` file with:

```
gemini_api_key=<api_key>
tavily_api_key=<api_key>
```

Run (PowerShell):

```
$env:PYTHONPATH = "."
```

Frontend:

```
streamlit run .\frontend\main.py
```

Backend:

```
python -m uvicorn app.main:app --reload
```

## 5. Contributing

Contributions are welcome, especially during this migration. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request, and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## 6. Security

Found a serious vulnerability? Please don't open a public issue — see [SECURITY.md](SECURITY.md) for how to report it responsibly.

## 7. License

This project is licensed under the [Apache License 2.0](LICENSE).