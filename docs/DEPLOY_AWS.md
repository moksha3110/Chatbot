# Milestone 15 — Deploying to AWS

This is the **architecture and runbook**. Run the commands yourself with your own
AWS account — they create **real, billable** resources.

> **Why this is a document, not an automated deploy:** provisioning cloud
> infrastructure is irreversible and costs money. It must be done deliberately,
> by the account owner, with credentials only you control.

---

## 1. The architecture (understand it before provisioning)

```
                         ┌─────────────────────────┐
   Browser  ───HTTPS──►  │  CloudFront (CDN)        │
                         └───────────┬─────────────┘
                          static /   │   /api/*
                    ┌───────────────┘   └────────────────┐
                    ▼                                     ▼
          ┌──────────────────┐                 ┌────────────────────┐
          │ S3 (React build) │                 │  Backend container │
          │  static hosting  │                 │  App Runner (ECR)  │
          └──────────────────┘                 └─────────┬──────────┘
                                                         │
                          ┌──────────────────────────────┼───────────────┐
                          ▼                               ▼               ▼
                 Secrets Manager               RDS PostgreSQL     Gemini API
                 (GEMINI_API_KEY)              (conversations)    (google-genai)
```

### What each piece is, and WHY

| Component | What | Why |
|-----------|------|-----|
| **ECR** | Elastic Container Registry | Stores your backend Docker image so AWS can run it |
| **App Runner** | Runs a container, gives an HTTPS URL, autoscales | Simplest way to run our backend image; no servers to manage |
| **S3** | Object storage w/ static website hosting | Cheapest, most reliable way to serve the React build |
| **CloudFront** | CDN + HTTPS + single entry point | Fast global delivery; routes `/` → S3 and `/api/*` → backend (so one domain, no CORS) |
| **Secrets Manager** | Encrypted secret storage | Keeps `GEMINI_API_KEY` out of images/env files; injected at runtime |
| **RDS (PostgreSQL)** | Managed SQL database | **Replaces SQLite** — see §4. Containers are ephemeral, so a file DB won't persist |

*Alternative to App Runner:* **ECS Fargate behind an Application Load Balancer**
— more control and features, more moving parts. App Runner is the right default
for an app this size.

---

## 2. Backend → ECR + App Runner

```bash
# Variables
export AWS_REGION=ap-south-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export REPO=aurum-backend

# 1. Create the image repository and log Docker in
aws ecr create-repository --repository-name $REPO --region $AWS_REGION
aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. Build and push the backend image
docker build -t $REPO ./backend
docker tag $REPO:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO:latest

# 3. Store the Gemini key as a secret
aws secretsmanager create-secret --name aurum/gemini-api-key \
  --secret-string "YOUR_REAL_GEMINI_API_KEY" --region $AWS_REGION
```

Then create an **App Runner service** (Console or CLI) from the ECR image:
- Port: **8000**
- Environment: reference the secret `aurum/gemini-api-key` as `GEMINI_API_KEY`,
  and set `GEMINI_MODEL`, `API_KEY`, `RATE_LIMIT_PER_MINUTE` as needed.
- App Runner gives you an HTTPS URL like `https://xxxx.awsapprunner.com`.

---

## 3. Frontend → S3 + CloudFront

```bash
# Build the React app to call the backend through CloudFront's /api path
cd frontend
VITE_API_BASE_URL=/api npm run build

# Create a bucket and upload the build
aws s3 mb s3://aurum-frontend-<unique-suffix>
aws s3 sync dist/ s3://aurum-frontend-<unique-suffix>
```

Create a **CloudFront distribution** with **two origins**:
1. the S3 bucket (default behavior `/*`), and
2. the App Runner URL (behavior `/api/*`), so API calls share the same domain
   as the site — exactly like nginx does in our Docker setup, and again **no CORS**.

Enable "SPA" behavior: map 403/404 to `/index.html` (200) so client routing works.

---

## 4. Production data — replace SQLite and the in-memory vector store

Our SQLite DB and in-memory vector store are perfect for development but **do not
survive container restarts or scale across instances**. For real deployment:

- **Conversations:** provision **RDS PostgreSQL**, put its URL in Secrets Manager,
  and update `app/services/memory.py` to use Postgres (e.g. via `psycopg`).
  Thanks to the layered design, **only that file changes**.
- **RAG vectors:** use **pgvector** (a Postgres extension) or **OpenSearch**; swap
  `app/rag/vector_store.py` to query it. Again, one file.

This is the concrete payoff of every "only this file changes" note earlier.

---

## 5. Before you spend money

- **Costs:** App Runner (~$5+/mo idle), RDS (~$15+/mo), CloudFront/S3 (pennies at
  low traffic). Set a **billing alarm** first.
- **Least privilege:** give App Runner an IAM role that can read *only* its secret.
- **Tear down** when done: delete the App Runner service, RDS instance, CloudFront
  distribution, S3 bucket, and ECR repo to stop charges.

---

*Not provisioned automatically: these steps create billable AWS resources and must
be run by the account owner. This document is the plan to do it safely.*
