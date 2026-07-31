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
│   ├── venv/            # Python virtual environment (NOT committed)
│   ├── main.py          # FastAPI app
│   ├── requirements.txt # Python dependencies
│   ├── .env             # Secrets — NOT committed
│   └── .env.example     # Template showing which env vars are needed
├── frontend/            # React + Vite app (Milestone 4)
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11+
- Git
- (Later) Node.js 18+ for the frontend

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
uvicorn main:app --reload
```

- API root:   http://127.0.0.1:8000/
- Interactive docs (Swagger UI):   http://127.0.0.1:8000/docs

## Environment variables

Copy `backend/.env.example` to `backend/.env` and fill in values.
**Never commit `.env` or real secret values.**

| Variable         | Required from | Description                     |
|------------------|---------------|---------------------------------|
| `GEMINI_API_KEY` | Milestone 3   | Google Gemini API key           |

## Current features

- ✅ **Milestone 1** — Project foundation (structure, venv, gitignore, README, Git/GitHub)
- ✅ Basic FastAPI backend with a `GET /` health check and a `POST /chat` echo endpoint

## Roadmap

Gemini integration → React chat UI → conversation engine → memory → prompt builder →
tool manager → weather tool → RAG → persistence → more tools → auth/logging → Docker → AWS.
