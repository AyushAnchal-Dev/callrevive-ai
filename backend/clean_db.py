import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def clean():
    print("Cleaning database tables...")
    async with AsyncSessionLocal() as db:
        tables = [
            "analytics_events",
            "revenue_predictions",
            "notifications",
            "appointments",
            "leads",
            "conversations",
            "calls",
            "customers"
        ]
        for table in tables:
            print(f"Truncating {table}...")
            await db.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))
        await db.commit()
    print("Database cleaned successfully!")

if __name__ == "__main__":
    asyncio.run(clean())
