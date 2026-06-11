# CallRevive AI — Testing Strategy

This document outlines the testing conventions, test execution environments, and testing methodologies for the CallRevive AI platform.

---

## 1. Test Architecture

The test suite is structured as follows under the `backend/tests/` folder:

*   **`conftest.py`**: Shared test environment setup, fixtures, and database transaction rollback setup.
*   **`unit/`**: Light unit tests targeting pure logic functions. External API calls (like Gemini and Redis) are fully mocked out.
    *   `test_lead_qualifier.py`: Asserts correct categorization of Gemini JSON responses.
    *   `test_revenue_predictor.py`: Validates revenue predicting prompts.
    *   `test_voice_handler.py`: Mocks Redis Dialogue controllers.
*   **`integration/`**: Integration tests asserting API responses, database writes, and webhook dispatches.
    *   `test_auth_endpoints.py`: Validates registration, login, and bearer auth headers.
    *   `test_webhook_endpoints.py`: Validates TwiML voice, WhatsApp, and recording callbacks.

---

## 2. Test Isolation & Database Transactions

To keep the test database clean and prevent test executions from polluting development states, we employ a **transactional rollback pattern** inside `conftest.py`:

1.  **Engine Disposal**: Before each test, the engine is disposed (`await async_engine.dispose()`). This binds the connection pool to the currently active asyncio loop, preventing loop conflicts.
2.  **Transaction Wrapping**: The test database fixture starts an async transaction:
    ```python
    async with async_engine.connect() as connection:
        transaction = await connection.begin()
        async_session = AsyncSession(bind=connection, expire_on_commit=False)
    ```
3.  **FastAPI Dependency Override**: We override the `get_db` dependency to yield this transactional session.
4.  **Automatic Rollback**: At the conclusion of each test, the transaction is rolled back, instantly reverting any inserts or updates.

---

## 3. Mocking Strategy

We use standard `unittest.mock.patch` decorators to mock external services:

*   **Gemini Client**: Patched at `app.ai.*.get_gemini_client` to mock responses.
*   **Redis Caching**: Patched in unit tests using mock async Redis instances.
*   **Celery tasks**: In integration webhook tests, task dispatches are mocked out using `.delay` patches. This allows us to verify that a task was successfully queued with correct parameters without running worker services.

---

## 4. Execution Commands

### Run Full Test Suite in Docker
```bash
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml run --rm api pytest -v
```

### Run Specific Test File
```bash
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml run --rm api pytest tests/integration/test_auth_endpoints.py -v
```
