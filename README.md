# 21STUDIO AI Agent

21STUDIO is a modern multi-provider AI Agent web application with a polished, responsive workspace UI.

## Stack

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Providers: Mistral, Groq, Cerebras
- Provider mode: Auto / manual selection
- Fallback: automatic provider failover
- Tool calling: local function tools
- Web search: public web search tool via `ddgs`
- Memory: persistent SQLite conversation memory
- Streaming: Server-Sent Events (SSE) token streaming

## Frontend experience

The frontend includes a premium dark workspace design with responsive layouts, animated ambient lighting, smooth message transitions, streaming cursors, provider switching, auto-growing composer, keyboard send, quick-start prompts, reduced-motion support, and mobile-friendly controls.

## Tools

- `calculate` — safe basic arithmetic evaluator (no Python `eval`)
- `web_search` — searches the public web and returns titles, URLs, and snippets to the agent

## Memory

Each chat is assigned a conversation ID. The backend stores user and assistant turns in a local SQLite database and reloads recent conversation history before each model call. The frontend keeps the active conversation ID in browser local storage and lets users start a new chat or clear memory.

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

Put provider keys in `backend/.env`, then start the API:

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

## Vercel deployment

Vercel has first-class support for Next.js and automatically detects Next.js build settings. For this repository, create a Vercel project from the GitHub repository and set **Root Directory** to `frontend`. Keep the default Next.js build command and output settings. citehttps://nextjs.org/learn/pages-router/deploying-nextjs-apphttps://vercel.com/frameworks/nextjs

Add this production environment variable in Vercel:

```text
NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-DOMAIN
```

The frontend must point to a publicly reachable backend. Provider API keys stay on the backend and must never use the `NEXT_PUBLIC_` prefix. Vercel documents that `NEXT_PUBLIC_*` values are exposed to the browser bundle. citehttps://vercel.com/academy/nextjs-foundations/env-and-security

After changing Vercel environment variables, redeploy so the new values are applied. citehttps://vercel.com/academy/vercel-foundations/vercel-settings

## Security

Keep provider API keys only in `backend/.env` or your backend hosting provider's secret/environment settings. Never commit secrets or put provider keys in the frontend.

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
- [x] Streaming responses
- [x] Premium responsive UI and animations
- [ ] Semantic long-term memory / RAG
