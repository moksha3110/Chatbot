# Internship Chatbot

A production-style AI chatbot built milestone-by-milestone as an internship project.
The goal is not just a working bot, but a **clean, modular, well-understood** architecture.

> ⚠️ Work in progress — being built one milestone at a time.

## Target architecture

```
USER
  ↓
React Frontend (Vite)            ← Milestone 4
  ↓  HTTP POST /chat
FastAPI Backend                  ← Milestone 2
  ↓
Conversation Engine              ← Milestone 5
  ↓
Prompt Builder                   ← Milestone 7
  ↓
Gemini API (google-genai)        ← Milestone 3
  ↓
AI Response  →  back to the user

(later) Tool Manager → Weather · Search · PDF/RAG · Calendar · Email · Maps · DB
```

## Tech stack

- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **AI:** Google Gemini via the official `google-genai` SDK *(added in Milestone 3)*
- **Frontend:** React + Vite *(added in Milestone 4)*
- **Config:** `python-dotenv` + `.env` for secrets
- **Version control:** Git + GitHub

## Project structure

```
internship-chatbot/
├── backend/
│   ├── venv/                 # Python virtual environment (NOT committed)
│   ├── app/                  # Application package (layered)
│   │   ├── main.py           # App factory: create app, CORS, include routes
│   │   ├── core/config.py    # Central configuration (reads .env)
│   │   ├── models/chat.py    # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── gemini_service.py  # Talks to the Gemini API
│   │   │   └── conversation.py    # Conversation engine (orchestrator)
│   │   └── api/routes.py     # HTTP endpoints (GET /, POST /chat)
│   ├── requirements.txt      # Python dependencies
│   ├── .env                  # Secrets — NOT committed
│   └── .env.example          # Template showing which env vars are needed
├── frontend/             # React + Vite chat UI
│   ├── src/
│   │   ├── App.jsx           # Chat logic + layout
│   │   ├── App.css           # Chat styling (teal + gold theme)
│   │   ├── index.css         # Global theme / palette variables
│   │   └── components/
│   │       ├── MessageBubble.jsx
│   │       └── TypingIndicator.jsx
│   ├── index.html
│   └── package.json
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+ (for the frontend)
- Git

## Backend setup

All commands run from the `backend/` folder.

```bash
cd backend

# 1. Create a virtual environment (isolated Python for this project)
python -m venv venv

# 2. Activate it
#    Windows (PowerShell):
venv\Scripts\Activate.ps1
#    macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your local secrets file from the template
copy .env.example .env      # Windows
# cp .env.example .env       # macOS / Linux
# then open .env and fill in your real values
```

## Running the backend

```bash
cd backend
uvicorn app.main:app --reload
```

- API root:   http://127.0.0.1:8000/
- Interactive docs (Swagger UI):   http://127.0.0.1:8000/docs

## Running the frontend

The app uses **two servers** at once: the FastAPI backend (port 8000) and the
Vite dev server (port 5173). Start the backend first, then in a **second terminal**:

```bash
cd frontend
npm install        # first time only
npm run dev
```

Open **http://localhost:5173** and start chatting.

> The browser (origin `localhost:5173`) calls the API (origin `127.0.0.1:8000`).
> These are different origins, so the backend enables **CORS** to allow it.
> By default the frontend calls `http://127.0.0.1:8000`; override with
> `VITE_API_BASE_URL` in `frontend/.env` if needed.

## Run with Docker

Requires Docker Desktop running. From the project root, with `GEMINI_API_KEY`
set in your shell (or a `.env` file beside `docker-compose.yml`):

```bash
docker compose up --build
```

- Frontend: http://localhost:8080  (nginx serves the built app and proxies `/api` → backend)
- Backend API: http://localhost:8000

Stop with `Ctrl+C`, or `docker compose down` to remove the containers.

## Environment variables

Copy `backend/.env.example` to `backend/.env` and fill in values.
**Never commit `.env` or real secret values.**

| Variable            | Location   | Description                                   |
|---------------------|------------|-----------------------------------------------|
| `GEMINI_API_KEY`    | backend    | Google Gemini API key (required)              |
| `GEMINI_MODEL`      | backend    | Model name (optional; default `gemini-flash-latest`) |
| `VITE_API_BASE_URL` | frontend   | Backend URL (optional; default `http://127.0.0.1:8000`) |

## Current features

- ✅ **Milestone 1** — Project foundation (structure, venv, gitignore, README, Git/GitHub)
- ✅ **Milestone 2** — Typed FastAPI backend: `GET /` health check, `POST /chat` with Pydantic models
- ✅ **Milestone 3** — Gemini integration via a dedicated `gemini_service.py` module
- ✅ **Milestone 4** — React + Vite chat UI (teal + gold theme) connected over CORS
- ✅ **Milestone 5** — Layered backend: `core` (config), `models`, `services` (gemini + conversation engine), `api` (routes)
- ✅ **Milestone 6** — Multi-turn conversation memory via session IDs and per-session history (in-memory; a "New Chat" button starts a fresh session)
- ✅ **Milestone 7** — Prompt builder: one module assembles system instruction + history + message (gives the bot a defined persona and rules)
- ✅ **Milestone 8** — Tool Manager foundation: generic tool interface + manual Gemini function calling, with one tool (`get_current_time`)
- ✅ **Milestone 9** — First real-time tool: `get_weather` (live data via the keyless Open-Meteo API); the model extracts the city argument itself
- ✅ **Milestone 10** — RAG: upload a PDF (`POST /documents`) → text extracted, chunked, embedded (Gemini), stored in an in-memory vector store; `/chat` retrieves relevant chunks to ground answers
- ✅ **Milestone 11** — Persistent storage: conversation history saved in SQLite (survives restarts); only `memory.py` changed thanks to the layered design
- ✅ **Milestone 12** — More tools: safe `calculate` (AST, no eval) and keyless `search_wikipedia`. Email/Calendar/Maps follow the same pattern but need credentials + side-effect safeguards
- ✅ **Milestone 13** — Production hardening: optional API-key auth (`X-API-Key`), per-IP rate limiting, input validation, logging, and a global error handler
- ✅ **Milestone 14** — Dockerized: backend image, frontend image (built + served by nginx that proxies `/api`), and a `docker-compose.yml` to run the whole stack
- ✅ **Milestone 15** — AWS deployment plan: full architecture + runbook in [docs/DEPLOY_AWS.md](docs/DEPLOY_AWS.md) (ECR + App Runner, S3 + CloudFront, Secrets Manager, RDS)

## Roadmap

Gemini integration → React chat UI → conversation engine → memory → prompt builder →
tool manager → weather tool → RAG → persistence → more tools → auth/logging → Docker → AWS.
