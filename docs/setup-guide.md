# CallRevive AI — Local Development Setup Guide

Follow this guide to set up the CallRevive AI platform locally for development and testing.

---

## Prerequisites
Before you begin, ensure you have the following installed on your machine:
*   [Docker & Docker Compose](https://www.docker.com/products/docker-desktop) (Active daemon)
*   [Git](https://git-scm.com/)

---

## 1. Obtain External Provider API Keys

CallRevive AI integrates with several cloud providers. You will need to sign up and obtain credentials:

### A. Google Gemini API Key
Used for Dialogue controllers, Lead Qualification, and Revenue Predictors.
1.  Go to [Google AI Studio](https://aistudio.google.com).
2.  Sign in with your Google account.
3.  Click **Create API Key**.
4.  Copy the generated key (used for `GEMINI_API_KEY`).

### B. Twilio Credentials & Sandbox Configuration
Used for Voice calls, speech-to-text, and WhatsApp chatbots.
1.  Sign up at [Twilio](https://www.twilio.com/try-twilio) (includes free trial credits).
2.  From your Twilio Console, copy:
    *   **Account SID** (used for `TWILIO_ACCOUNT_SID`)
    *   **Auth Token** (used for `TWILIO_AUTH_TOKEN`)
3.  Buy a Twilio phone number (or use the trial one) (used for `TWILIO_PHONE_NUMBER`).
4.  Navigate to **Messaging > Try it out > Send a WhatsApp message** to set up the WhatsApp Sandbox. Join the sandbox using your mobile device and copy the sandbox phone number (used for `TWILIO_WHATSAPP_NUMBER` e.g., `whatsapp:+14155238886`).

### C. PostgreSQL Database (Neon)
Used for primary relational data storage.
1.  Go to [Neon Console](https://neon.tech) and create a free project.
2.  Copy your async connection string (used for `DATABASE_URL` with `postgresql+asyncpg://...`) and sync connection string (used for `DATABASE_SYNC_URL` with `postgresql://...`).

### D. Redis (Upstash)
Used for dialogue session memory caching.
1.  Go to [Upstash Console](https://upstash.com) and create a free Redis database.
2.  Copy the connection string (used for `REDIS_URL`).

### E. RabbitMQ Broker (CloudAMQP)
Used for message queuing of async worker tasks.
1.  Go to [CloudAMQP Console](https://www.cloudamqp.com) and register for a free account.
2.  Create a free "Little Lemur" instance.
3.  Copy the AMQP URL (used for `CLOUDAMQP_URL`).

### F. Object Storage (Backblaze B2)
Used for uploading and storing audio call recordings.
1.  Go to [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html) and create a free account.
2.  Create a bucket named `callrevive-recordings` and copy the Bucket ID and Name.
3.  Navigate to App Keys, generate a master/application key, and copy the Key ID and Application Key.

---

## 2. Configuration Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-org/callrevive-ai.git
    cd callrevive-ai
    ```
2.  Create a `.env` file in the `backend/` directory by copying `.env.example`:
    ```bash
    cp backend/.env.example backend/.env
    ```
3.  Fill in all the environment variables in `backend/.env` with your collected credentials.

---

## 3. Running Locally with Docker Compose

To boot up the entire development stack (FastAPI backend, Celery worker, Redis cache, RabbitMQ queue, and Postgres DB):

1.  Spin up the containers:
    ```bash
    docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml up -d
    ```
2.  Verify the running status:
    ```bash
    docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml ps
    ```
    All containers (`api`, `worker`, `postgres`, `redis`, `rabbitmq`) should have status `Up` or `healthy`.

3.  Apply database migrations to sync the schema:
    ```bash
    docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml run --rm api alembic upgrade head
    ```

---

## 4. Run the Test Suite

To run all unit and integration tests inside the test environment container:
```bash
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml run --rm api pytest -v
```

---

## 5. Local Frontend Development (If Node is installed)

1.  Navigate to the frontend folder and install npm packages:
    ```bash
    cd frontend
    npm install
    ```
2.  Start the development server:
    ```bash
    npm run dev
    ```
3.  Open browser at `http://localhost:5173` to interact with the dashboard.
