import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        tables = ["customers", "calls", "conversations", "leads", "appointments", "notifications"]
        for table in tables:
            count = (await db.execute(text(f"SELECT COUNT(*) FROM {table}"))).scalar()
            print(f"{table}: {count} records")

if __name__ == "__main__":
    asyncio.run(check())
