# RAG Chatbot

A full-stack Retrieval-Augmented Generation (RAG) chatbot that lets users upload PDF documents and ask questions about their content. Built with FastAPI, LangChain, LangGraph, and React.

## Features

- **PDF ingestion** — upload PDFs that are chunked, embedded, and stored in a vector database
- **RAG pipeline** — questions are answered using relevant document context retrieved via similarity search
- **Streaming responses** — answers stream token by token via server-sent events
- **Conversation history** — multi-turn chat with persistent history per conversation
- **Prompt versioning** — prompts are managed and versioned via LangSmith
- **Observability** — full LangSmith tracing for every inference run
- **Auth** — JWT-based authentication with user accounts

## Architecture

```
client/ (React + Vite + TypeScript)
    └── REST + SSE  →  app/ (FastAPI)
                            ├── auth router
                            ├── chat router   →  LangGraph RAG pipeline
                            ├── upload router →  PDF chunking + PGVector
                            └── conversations router
app/
    ├── services/
    │   ├── chat_service.py       — LangGraph graph execution & streaming
    │   ├── upload_service.py     — PDF parsing + embedding
    │   ├── prompt_registry.py    — LangSmith prompt versioning
    │   └── auth_service.py       — JWT handling
    ├── db/                       — SQLAlchemy models (users, conversations, messages)
    └── repository/               — data access layer
```

**RAG pipeline (LangGraph)**

```
question → [retrieve] → similarity search on PGVector
         → [generate] → LLM (Gemini) with context + history
         → streamed answer
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python |
| LLM | Google Gemini (via `langchain-google-genai`) |
| Orchestration | LangChain, LangGraph |
| Vector store | PGVector (PostgreSQL) |
| Database | PostgreSQL (Neon) + SQLAlchemy + Alembic |
| Observability | LangSmith |
| Frontend | React 19, TypeScript, Vite |
| Auth | JWT (`python-jose`) |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL with the `pgvector` extension (or a [Neon](https://neon.tech) database)
- A [Google AI Studio](https://aistudio.google.com) API key
- A [LangSmith](https://smith.langchain.com) API key (for tracing and prompt versioning)

### Backend

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and fill in environment variables
cp .env.example .env   # or create .env manually (see below)

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Frontend

```bash
cd client

# Install dependencies
npm install

# Copy and configure environment variables
cp .env.example .env.local

# Start the dev server
npm run dev
```

The app will be available at `http://localhost:5173`.

## Environment Variables

Create a `.env` file in the project root:

```env
# PostgreSQL connection string (asyncpg driver)
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname?ssl=require

# Google Gemini API key
GOOGLE_API_KEY=your-google-api-key

# LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=rag-chatbot
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# JWT settings
JWT_SECRET=change-me-in-production

# Prompt versioning (optional)
PROMPT_CACHE_TTL_SECONDS=300
PROMPT_FORCE_VERSION=
PROMPT_EXPERIMENT_VERSION=
PROMPT_EXPERIMENT_ROLLOUT=0
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive a JWT |
| `POST` | `/upload` | Upload a PDF to a named collection |
| `POST` | `/chat` | Send a message (streams SSE response) |
| `GET` | `/conversations` | List conversations for the current user |
| `GET` | `/conversations/{id}/messages` | Get messages in a conversation |
| `DELETE` | `/conversations/{id}` | Delete a conversation |

A Postman collection is included at [`postman_collection.json`](postman_collection.json).

## Database Migrations

Migrations are managed with Alembic:

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"

# Roll back one step
alembic downgrade -1
```

## Prompt Versioning

Prompts are stored and versioned in LangSmith. The `PromptRegistry` service resolves the active prompt version at runtime, with optional A/B experimentation controlled by `PROMPT_EXPERIMENT_VERSION` and `PROMPT_EXPERIMENT_ROLLOUT`. To push a new prompt version:

```bash
python app/scripts/push_prompt.py
```

## License

[MIT](LICENSE)
