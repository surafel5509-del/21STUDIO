# 21STUDIO AI Agent

21STUDIO is a multi-provider AI Agent web application built for the web.

## Stack

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Providers: Mistral, Groq, Cerebras
- Provider mode: Auto / manual selection

## Project structure

```text
21STUDIO/
├── frontend/
│   └── app/
├── backend/
│   └── app/
│       ├── agent/
│       ├── providers/
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

## Security

Keep provider API keys only in `backend/.env`. Never commit secrets or put provider keys in the frontend.

## Roadmap

1. Connect real Mistral, Groq, and Cerebras SDK calls.
2. Add automatic fallback and health-aware routing.
3. Add agent planning, tools, memory, and streaming responses.
