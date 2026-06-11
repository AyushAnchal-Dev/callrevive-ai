import os
import sys
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

# Add backend directory to sys.path so we can import the app
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Detect if we are inside docker or default to docker services
db_host = "postgres"
redis_host = "redis"

# Setup environment variables for test execution
os.environ["APP_ENV"] = "testing"
os.environ["APP_DEBUG"] = "true"
os.environ["DATABASE_URL"] = f"postgresql+asyncpg://callrevive:callrevive_dev@{db_host}:5432/callrevive"
os.environ["DATABASE_SYNC_URL"] = f"postgresql://callrevive:callrevive_dev@{db_host}:5432/callrevive"
os.environ["REDIS_URL"] = f"redis://{redis_host}:6379/0"
os.environ["GEMINI_API_KEY"] = "test-gemini-key"
os.environ["JWT_SECRET"] = "test-jwt-secret"
os.environ["TWILIO_AUTH_TOKEN"] = ""

# Import app components after environment variables are set
from app.main import app
from app.db.session import async_engine, get_db

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db() -> AsyncSession:
    """Fixture that wraps database operations in a transaction and rolls it back."""
    await async_engine.dispose()
    async with async_engine.connect() as connection:
        transaction = await connection.begin()
        async_session = AsyncSession(bind=connection, expire_on_commit=False)
        
        async def _get_db_override():
            yield async_session
            
        app.dependency_overrides[get_db] = _get_db_override
        
        yield async_session
        
        app.dependency_overrides.pop(get_db, None)
        await transaction.rollback()

@pytest.fixture
async def client(db) -> AsyncClient:
    """Fixture that provides an AsyncClient connected to the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac
