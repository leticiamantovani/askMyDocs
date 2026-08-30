# askMyDocs

A full-stack Retrieval-Augmented Generation (RAG) chatbot that lets users upload PDF documents and ask questions about their content. Answers stream token-by-token and are grounded in the uploaded documents via vector similarity search.

Built with FastAPI, LangChain, LangGraph, Google Gemini, and React 19.

---
# Demo

https://ask-my-docs-cyan.vercel.app/login
---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [RAG Pipeline](#rag-pipeline)
- [Authentication](#authentication)
- [Prompt Versioning](#prompt-versioning)
- [Database Migrations](#database-migrations)
- [Frontend](#frontend)

---

## Features

- **PDF ingestion** — upload PDFs that are parsed, chunked, embedded, and stored in a vector database
- **RAG pipeline** — questions are answered using relevant document context retrieved via similarity search
- **Streaming responses** — answers stream token by token via Server-Sent Events (SSE)
- **Conversation history** — multi-turn chat with persistent history per conversation
- **Document management** — list and delete uploaded documents; each document has its own vector collection
- **Prompt versioning** — prompts are managed and versioned via LangSmith with TTL caching and A/B rollout support
- **Observability** — full LangSmith tracing for every inference run
- **Auth** — JWT-based authentication with user accounts, password reset via email, and profile management
- **Bug reporting** — in-app bug report form routed to a configurable email

---

## Architecture

```
client/ (React 19 + Vite + TypeScript)
    └── REST + SSE  →  app/ (FastAPI)
                            ├── /auth        → register, login, profile, password reset
                            ├── /chat        → streaming RAG answer (SSE)
                            ├── /upload      → PDF ingestion pipeline
                            ├── /documents   → list & delete documents
                            ├── /conversations → conversation & message history
                            └── /feedback    → bug reports via email

app/
    ├── routers/        HTTP handlers (thin layer, delegates to services)
    ├── services/       Business logic (auth, chat, upload, conversations, email, prompts)
    ├── repository/     Data access layer (conversations, messages, documents)
    ├── db/             SQLAlchemy models + async session + PGVector store
    ├── ingestion/      PDF loader → text splitter → vector indexer
    ├── rag/            LangGraph pipeline (retrieve → augment → generate)
    ├── llm/            Gemini client + streaming utilities
    ├── core/           Config, dependency injection, custom exceptions
    └── schema/         Pydantic DTOs for request/response validation
```

### RAG Pipeline (LangGraph)

```
question
  │
  ▼
[retrieve]  →  embed question → PGVector similarity search (top-10 chunks)
  │
  ▼
[augment]   →  fetch prompt from LangSmith → format with context + history + question
  │
  ▼
[generate]  →  Google Gemini 2.5 Flash → stream tokens back to client
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11+ |
| LLM | Google Gemini 2.5 Flash |
| Embeddings | Google Gemini Embedding (768-dim) |
| Orchestration | LangChain, LangGraph |
| Vector store | PostgreSQL + pgvector extension |
| Relational DB | PostgreSQL (Neon or self-hosted) + SQLAlchemy async + Alembic |
| Observability | LangSmith (tracing + prompt versioning) |
| Auth | JWT (python-jose + HS256), bcrypt |
| Email | Mailtrap |
| Frontend | React 19, TypeScript, Vite, React Router, React Dropzone, React Markdown |
| API communication | REST + Server-Sent Events |

---

## Project Structure

```
askMyDocs/
├── app/
│   ├── main.py                        # FastAPI app init, CORS, router registration
│   ├── routers/
│   │   ├── auth.py                    # Auth endpoints (register, login, profile, password reset)
│   │   ├── chat.py                    # Streaming chat endpoint
│   │   ├── upload.py                  # PDF upload endpoint
│   │   ├── documents.py               # Document listing and deletion
│   │   ├── conversations.py           # Conversation and message management
│   │   └── feedback.py                # Bug report submission
│   ├── services/
│   │   ├── auth_service.py            # JWT, bcrypt, user registration/login/reset
│   │   ├── chat_service.py            # LangGraph execution and SSE streaming
│   │   ├── conversation_service.py    # Conversation CRUD
│   │   ├── upload_service.py          # PDF parse → chunk → embed → store
│   │   ├── email_service.py           # Password reset and bug report emails (Mailtrap)
│   │   └── prompt_registry.py         # LangSmith prompt cache + A/B rollout
│   ├── repository/
│   │   ├── conversation_repository.py
│   │   ├── message_repository.py
│   │   └── document_repository.py     # Includes async vector store cleanup on delete
│   ├── db/
│   │   ├── session.py                 # AsyncSession factory
│   │   ├── vector_store.py            # PGVector init
│   │   └── models/
│   │       ├── users.py
│   │       ├── conversations.py
│   │       ├── messages.py
│   │       └── documents.py
│   ├── ingestion/
│   │   ├── loader.py                  # PDF text extraction (pypdf)
│   │   ├── splitter.py                # RecursiveCharacterTextSplitter (500 tokens, 50 overlap)
│   │   └── indexer.py                 # Embed chunks and store in PGVector
│   ├── rag/
│   │   ├── pipeline.py                # LangGraph StateGraph definition
│   │   ├── retriever.py               # Vector similarity search (k=10)
│   │   └── prompt_builder.py          # Prompt formatting with history + context
│   ├── llm/
│   │   ├── client.py                  # Gemini chat model + embedding model
│   │   └── streaming.py               # LangGraph event streaming utilities
│   ├── core/
│   │   ├── config.py                  # pydantic-settings env var loading
│   │   ├── dependencies.py            # FastAPI dependency injection
│   │   └── exceptions.py              # DomainError hierarchy
│   └── schema/
│       ├── auth.py
│       ├── chat.py
│       ├── conversations.py
│       └── documents.py
├── client/                            # React frontend (see Frontend section)
├── alembic/                           # Database migrations
├── alembic.ini
├── requirements.txt
└── postman_collection.json
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL with the `pgvector` extension (or a [Neon](https://neon.tech) database — free tier works)
- [Google AI Studio](https://aistudio.google.com) API key (for Gemini LLM + embeddings)
- [LangSmith](https://smith.langchain.com) API key (for tracing and prompt management)
- [Mailtrap](https://mailtrap.io) API key (optional — only needed for password reset emails)

### Backend

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env   # then fill in the values (see Environment Variables below)

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd client

# Install dependencies
npm install

# Configure environment variables
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start the dev server
npm run dev
```

App available at `http://localhost:5173`.

---

## Environment Variables

Create a `.env` file in the project root:

```env
# PostgreSQL (asyncpg driver required)
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname?ssl=require

# Google Gemini (LLM + embeddings)
GOOGLE_API_KEY=your-google-api-key

# LangSmith (tracing + prompt versioning)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=rag-chatbot
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# JWT
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=604800   # 7 days

# Email (Mailtrap)
MAILTRAP_API_KEY=your-mailtrap-key
BUG_REPORT_EMAIL=your@email.com
FRONTEND_URL=http://localhost:5173

# Password reset
RESET_TOKEN_EXPIRE_MINUTES=30

# Prompt versioning (optional)
PROMPT_CACHE_TTL_SECONDS=300
PROMPT_FORCE_VERSION=           # override all users to a specific prompt version
PROMPT_EXPERIMENT_VERSION=      # A/B test prompt version
PROMPT_EXPERIMENT_ROLLOUT=0     # % of users that get the experiment version (0–100)
```

---

## API Reference

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | — | Create account |
| `POST` | `/auth/login` | — | Login → returns JWT |
| `GET` | `/auth/me` | JWT | Get current user profile |
| `PATCH` | `/auth/me` | JWT | Update name/email |
| `PATCH` | `/auth/me/password` | JWT | Change password |
| `POST` | `/auth/forgot-password` | — | Request password reset email |
| `POST` | `/auth/reset-password` | — | Reset password with token |

### Documents

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/upload` | JWT | Upload a PDF; triggers ingestion pipeline |
| `GET` | `/documents` | JWT | List user's documents |
| `DELETE` | `/documents/{id}` | JWT | Delete document and its vector embeddings |

### Chat

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/chat` | JWT | Send message; streams SSE response. Response header `X-Conversation-ID` returns the conversation ID. Body: `{ question, document_id?, conversation_id? }` |

### Conversations

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/conversations` | JWT | List conversations |
| `POST` | `/conversations` | JWT | Create conversation |
| `GET` | `/conversations/{id}` | JWT | Get conversation with messages |
| `GET` | `/conversations/{id}/messages` | JWT | List messages |
| `DELETE` | `/conversations/{id}` | JWT | Delete conversation |

### Feedback

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/feedback/bug` | optional | Submit a bug report |

A full [Postman collection](postman_collection.json) is included.

---

## RAG Pipeline

The pipeline is implemented as a 3-node [LangGraph](https://langchain-ai.github.io/langgraph/) `StateGraph`:

```python
RAGState = {
    "question": str,
    "collection_name": str,      # PGVector collection, e.g. "user_{uid}_{doc_id}"
    "conversation_id": UUID,
    "history": list[Message],    # prior messages in conversation
    "context": str,              # retrieved document chunks
    "answer": str,               # prompt or final LLM response
    "user_id": str | None,
    "user_name": str | None,
}
```

**Nodes:**

1. **`retrieve`** — embeds the question via Google Gemini Embedding, runs similarity search in PGVector (top-10 chunks), concatenates results into `context`
2. **`augment`** — fetches the active prompt template from LangSmith (with caching), formats it with `context`, `history`, `question`, and `user_name`
3. **`generate`** — calls Google Gemini 2.5 Flash, streams tokens back via `on_chat_model_stream` events

Streaming is handled through SSE: the `chat` router returns a `StreamingResponse`, and the frontend consumes it with `ReadableStream`.

---

## Authentication

- **Standard**: JWT Bearer token (HS256, 7-day TTL)
- **Flow**: `POST /auth/login` → `{ access_token }` → store in `localStorage` → `Authorization: Bearer <token>` on every request
- **Password reset**: generates a 32-char URL-safe token (30-min TTL), stores in DB, sends email with reset link via Mailtrap
- **Protected routes**: `get_current_user` FastAPI dependency decodes and validates the JWT; raises 401 on failure
- **Frontend**: `api.ts` injects the auth header automatically and redirects to `/login` on 401

---

## Prompt Versioning

Prompts are stored and versioned externally in [LangSmith Hub](https://smith.langchain.com). `PromptRegistry` is a singleton that:

- Fetches and caches prompts with a configurable TTL (`PROMPT_CACHE_TTL_SECONDS`, default 300s)
- Supports **emergency override**: `PROMPT_FORCE_VERSION` pins all users to a specific version
- Supports **A/B testing**: `PROMPT_EXPERIMENT_VERSION` + `PROMPT_EXPERIMENT_ROLLOUT` route a percentage of users to an experimental prompt (bucketed by MD5 hash of `user_id`)

To push a new prompt version to LangSmith:

```bash
python app/scripts/push_prompt.py
```

---

## Database Migrations

Migrations are managed with [Alembic](https://alembic.sqlalchemy.org):

```bash
# Apply all pending migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1

# Generate a new migration from model changes
alembic revision --autogenerate -m "description"
```

Migration history (in order):

1. Create `conversations` and `messages` tables
2. Convert IDs to UUID
3. Create `users` table
4. Add `user_id` and `title` to conversations
5. Create `documents` table
6. Add `reset_token` and `reset_token_expires` to users
7. Add `name` to users
8. Add `document_id` FK to conversations

---

## Frontend

**Stack**: React 19, TypeScript, Vite, React Router DOM, React Dropzone, React Markdown

### Pages

| Route | Component | Description |
|---|---|---|
| `/login` | `LoginPage` | Email/password login |
| `/forgot-password` | `ForgotPasswordPage` | Request password reset |
| `/reset-password` | `ResetPasswordPage` | Submit new password with token |
| `/profile` | `ProfilePage` | Update name, email, password |
| `/` | Main chat UI | Conversation + document sidebar + chat |

### Key Components

| Component | Description |
|---|---|
| `ConversationSidebar` | Lists conversations, handles new/delete |
| `DocumentSelector` | Lists uploaded PDFs, handles select/delete |
| `PdfDropzone` | Drag-and-drop PDF upload with progress |
| `MessageList` | Renders messages with Markdown support |
| `ChatInput` | Message textarea + submit |
| `BugReportButton` | In-app bug report modal |
| `ConfirmModal` | Reusable confirmation dialog |

### `useChat` Hook

Manages all chat state:
- Optimistic message updates while streaming
- Session key-based history reset when switching conversations/documents
- Abort controller for in-flight SSE requests
- Extracts `X-Conversation-ID` from response headers to track new conversations

---

## License

[MIT](LICENSE)
