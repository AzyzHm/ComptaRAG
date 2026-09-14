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
 An agentic RAG assistant for accounting and financial-law questions, combining IFRS knowledge with Tunisian tax and accounting regulations, and grounding every answer in retrieved source material.
</p>

---

## Table of contents

1. [Project overview](#1-project-overview)
2. [Getting started](#2-getting-started)
3. [Contributing](#3-contributing)
4. [Security](#4-security)
5. [License](#5-license)

## 1. Project overview

ComptaRAG is an agentic RAG assistant for accounting and financial-law questions, aimed especially at professionals in Tunisia. It combines IFRS knowledge with Tunisian tax and accounting regulations, and grounds every answer in retrieved source material instead of relying on the model's own memory.

The project has two parts:

- **Angular frontend** (`frontend/`): a public landing page, sign-in/sign-up, the chat interface (with a chat history sidebar, at `/chat` and `/chat/:chatId`), and an admin page for managing user roles. The UI supports light, dark, and system themes, and the layout is responsive down to mobile. See the [frontend README](frontend/README.md) for the stack, project structure, theming, and responsive-layout conventions.
- **FastAPI backend** (`backend/`): a LangGraph agent that routes each question, retrieves relevant context from a ChromaDB vector store (embedded locally via Ollama), falls back to a Tavily web search when local context is not enough, and generates the final answer with Gemini. Every route is rate limited to guard against abuse. See the [backend README](backend/README.md) for the pipeline, authentication and roles, the data model, rate limiting, and project structure.

Authentication is handled by Firebase: the frontend signs users in with the Firebase JS SDK (email and password, or Google), and the backend verifies the resulting ID token with the Firebase Admin SDK on every request. See the [backend README's roles section](backend/README.md#5-roles-and-authorization) for how roles work, and its [Firebase setup section](backend/README.md#2-getting-started) for setting up a project.

## 2. Getting started

Clone the repository, then set up each part:

- **Backend**: see the [backend README's getting started section](backend/README.md#2-getting-started), it covers the Python environment, environment variables, Ollama, building the local knowledge base, running the API, and setting up the shared Firebase project.
- **Frontend**: see the [frontend README's getting started section](frontend/README.md#2-getting-started), it covers `npm install`, the dev server, and the Firebase web config.

Both need to point at the same Firebase project, so set that up first from the backend README's Firebase setup steps.

## 3. Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request, and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## 4. Security

Every route is rate limited by IP address, with a stricter limit on `POST /chats/{id}/messages` (the route that triggers the full RAG/LLM pipeline) and on `/auth/me` (hit right after every sign-in). Sign-up and sign-in themselves go straight from the frontend to Firebase Authentication and are not backend routes, so they are protected by Firebase's own abuse controls rather than anything in this repository. See the [backend README's rate-limiting section](backend/README.md#7-rate-limiting) for the full list of limits and how to tune them.

Found a serious vulnerability? Please do not open a public issue, see [SECURITY.md](SECURITY.md) for how to report it responsibly.

## 5. License

This project is licensed under the [Apache License 2.0](LICENSE).