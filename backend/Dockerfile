# Backend image: a small Python base with our app and dependencies baked in.
#
# An IMAGE is a snapshot (this file's result); a CONTAINER is a running instance
# of that image. We build once, then run one or many containers from it.

FROM python:3.11-slim

# Where our code lives inside the container.
WORKDIR /app

# Install dependencies FIRST (as its own layer) so Docker can cache them: if only
# our code changes, it won't reinstall packages on every rebuild.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY app ./app

# Document the port the app listens on (informational).
EXPOSE 8000

# Bind to 0.0.0.0 (not 127.0.0.1) so the app is reachable from OUTSIDE the
# container. The GEMINI_API_KEY is injected at run time, never baked into the image.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
