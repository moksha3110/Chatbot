# Chatbot

A minimal FastAPI chatbot backend.

## Flow

```
Browser  ->  FastAPI  ->  POST /chat  ->  JSON response
```

## Endpoints

| Method | Path    | Body                     | Response                          |
|--------|---------|--------------------------|-----------------------------------|
| GET    | `/`     | –                        | `{"status": "Chatbot backend is running"}` |
| POST   | `/chat` | `{"message": "hi"}`      | `{"response": "You said: hi"}`    |

## Run locally

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # then add your key
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API docs.
