# 21STUDIO AI Agent

21STUDIO is a multi-provider AI Agent web application built for the web.

## Stack

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Providers: Mistral, Groq, Cerebras
- Provider mode: Auto / manual selection
- Fallback: automatic provider failover
- Tool calling: local function tools
- Web search: public web search tool via `ddgs`
- Memory: persistent SQLite conversation memory

## Tools

- `calculate` — safe basic arithmetic evaluator (no Python `eval`)
- `web_search` — searches the public web and returns titles, URLs, and snippets to the agent

The agent can decide when to call a tool, execute it locally, return the tool result to the model, and continue until a final answer is produced.

## Memory

Each chat is assigned a conversation ID. The backend stores user and assistant turns in a local SQLite database and reloads the recent conversation history before each model call. This means conversation context survives backend restarts.

The frontend keeps the active conversation ID in browser local storage. Users can start a new chat or permanently clear the current conversation through the UI.

The database defaults to `backend/data/memory.db` and is ignored by Git. You can override it with `MEMORY_DB_PATH` in `backend/.env`.

For larger production deployments, the SQLite layer can later be replaced with PostgreSQL or another database. FastAPI supports using SQL databases through libraries such as SQLModel. citeturn0search0

## Project structure

```text
21STUDIO/
├── frontend/
│   └── app/
├── backend/
│   └── app/
│       ├── agent/
│       │   ├── agent.py
│       │   ├── tool_loop.py
│       │   └── tools.py
│       ├── memory.py
│       ├── providers/
│       └── routes/
│           ├── chat.py
│           ├── health.py
│           └── memory.py
├── .gitignore
└── README.md
```

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```

Put your provider keys in `backend/.env` and optionally configure `MEMORY_DB_PATH`.

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Provider fallback

The agent tries configured providers in the requested order. If a provider is unavailable, errors, times out, or is rate-limited, the agent automatically tries the next configured provider.

## Web search

Web search is implemented as a normal local function tool, so it works with the existing Mistral, Groq, and Cerebras provider router instead of locking the whole agent to one provider. Search results are passed back to the model as structured JSON containing a query, title, URL, and snippet.

## Security

Keep provider API keys only in `backend/.env`. Never commit secrets or put provider keys in the frontend. The local memory database is also ignored by Git.

## Current milestone

- [x] FastAPI backend
- [x] Next.js frontend
- [x] Mistral integration
- [x] Groq integration
- [x] Cerebras integration
- [x] Automatic fallback routing
- [x] Tool calling
- [x] Web search
- [x] Persistent conversation memory
- [ ] Streaming responses
- [ ] Semantic long-term memory / RAG
