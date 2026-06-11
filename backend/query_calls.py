import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.call import Call
from app.models.customer import Customer
from app.models.lead import Lead
from app.models.notification import Notification

async def query():
    async with AsyncSessionLocal() as db:
        print("=== RECENT CALLS ===")
        calls = (await db.execute(select(Call).order_by(Call.started_at.desc()))).scalars().all()
        for c in calls:
            print(f"Call ID: {c.id} | Twilio SID: {c.twilio_call_sid} | From: {c.from_number} | To: {c.to_number} | Direction: {c.direction} | Status: {c.status} | Started: {c.started_at}")
            
        print("\n=== RECENT CUSTOMERS ===")
        customers = (await db.execute(select(Customer).order_by(Customer.first_contact_at.desc()))).scalars().all()
        for cust in customers:
            print(f"Customer ID: {cust.id} | Phone: {cust.phone_number} | Category: {cust.category} | Created: {cust.first_contact_at}")

        print("\n=== RECENT LEADS ===")
        leads = (await db.execute(select(Lead).order_by(Lead.created_at.desc()))).scalars().all()
        for l in leads:
            print(f"Lead ID: {l.id} | Customer ID: {l.customer_id} | Status: {l.status} | Lead Score: {l.lead_score} | Revenue: {l.estimated_revenue} | Created: {l.created_at}")

        print("\n=== RECENT NOTIFICATIONS ===")
        notifications = (await db.execute(select(Notification).order_by(Notification.created_at.desc()))).scalars().all()
        for n in notifications:
            print(f"Notification ID: {n.id} | User ID: {n.user_id} | Type: {n.type} | Title: {n.title} | Sent: {n.sent_at} | Created: {n.created_at}")

if __name__ == "__main__":
    asyncio.run(query())
