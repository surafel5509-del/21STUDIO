# 21STUDIO AI Agent

21STUDIO is a multi-provider AI Agent web application built for the web.

## Stack

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Providers: Mistral, Groq, Cerebras
- Provider mode: Auto / manual selection
- Fallback: automatic provider failover

## Project structure

```text
21STUDIO/
├── frontend/
│   └── app/
├── backend/
│   └── app/
│       ├── agent/
│       ├── providers/
│       │   ├── mistral.py
│       │   ├── groq.py
│       │   ├── cerebras.py
│       │   └── router.py
│       └── routes/
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

Put your provider keys in `backend/.env`:

```env
MISTRAL_API_KEY=your_key
GROQ_API_KEY=your_key
CEREBRAS_API_KEY=your_key
DEFAULT_PROVIDER=auto
PROVIDER_ORDER=cerebras,groq,mistral
FRONTEND_URL=http://localhost:3000
```

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

## Security

Keep provider API keys only in `backend/.env`. Never commit secrets or put provider keys in the frontend.

## Current milestone

- [x] FastAPI backend
- [x] Next.js frontend
- [x] Mistral integration
- [x] Groq integration
- [x] Cerebras integration
- [x] Automatic fallback routing
- [ ] Streaming responses
- [ ] Tool calling
- [ ] Memory
- [ ] Web search
