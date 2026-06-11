import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from decimal import Decimal

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.business import Business
from app.models.customer import Customer
from app.models.call import Call, CallDirection, CallStatus
from app.models.conversation import Conversation, ConversationChannel, ConversationStatus
from app.models.lead import Lead
from app.models.appointment import Appointment
from app.models.notification import Notification
from app.models.revenue_prediction import RevenuePrediction
from app.models.analytics_event import AnalyticsEvent


async def seed():
    print("Starting database seeding...")
    async with AsyncSessionLocal() as db:
        # 1. Create Test User
        email = "test@example.com"
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print("Creating test user...")
            user = User(
                email=email,
                password_hash=hash_password("password123"),
                full_name="Test Business Owner",
                role="admin",
                phone_number="+18392616744",
                is_active=True,
            )
            db.add(user)
            await db.flush()
        else:
            print("Test user already exists.")

        # 2. Create Business
        result = await db.execute(select(Business).where(Business.owner_id == user.id))
        business = result.scalar_one_or_none()

        if not business:
            print("Creating business...")
            business = Business(
                name="CallRevive Home Services",
                category="Home Services",
                phone_number="+18392616744",
                whatsapp_number="+14155238886",
                email=email,
                owner_id=user.id,
                timezone="Asia/Kolkata",
                is_active=True,
            )
            db.add(business)
            await db.flush()
            user.business_id = business.id
            db.add(user)
            await db.flush()
        else:
            print("Business already exists.")

        # 3. Create Customers
        customers_data = [
            {"name": "Rajesh Kumar", "phone_number": "+919876543210", "email": "rajesh@example.com", "category": "vip"},
            {"name": "Priya Sharma", "phone_number": "+919876543211", "email": "priya@example.com", "category": "returning"},
            {"name": "Amit Patel", "phone_number": "+919876543212", "email": "amit@example.com", "category": "new"},
            {"name": "Sarah Jenkins", "phone_number": "+15550199", "email": "sarah@example.com", "category": "vip"},
            {"name": "John Doe", "phone_number": "+15550123", "email": "john@example.com", "category": "new"},
        ]

        customers = {}
        for c_data in customers_data:
            result = await db.execute(
                select(Customer).where(
                    Customer.phone_number == c_data["phone_number"],
                    Customer.business_id == business.id
                )
            )
            cust = result.scalar_one_or_none()
            if not cust:
                print(f"Creating customer {c_data['name']}...")
                cust = Customer(
                    name=c_data["name"],
                    phone_number=c_data["phone_number"],
                    email=c_data["email"],
                    business_id=business.id,
                    category=c_data["category"],
                    first_contact_at=datetime.now(timezone.utc) - timedelta(days=10),
                    last_contact_at=datetime.now(timezone.utc) - timedelta(hours=2),
                )
                db.add(cust)
                await db.flush()
            else:
                print(f"Customer {cust.name} already exists.")
            customers[c_data["name"]] = cust

        # 4. Create Calls
        calls_data = [
            {
                "customer": "Rajesh Kumar",
                "direction": CallDirection.INBOUND,
                "status": CallStatus.MISSED,
                "sid": "CA11111111111111111111111111111111",
                "offset_hours": 3,
                "duration": 0
            },
            {
                "customer": "Rajesh Kumar",
                "direction": CallDirection.OUTBOUND,
                "status": CallStatus.CALLBACK_COMPLETED,
                "sid": "CA11111111111111111111111111111112",
                "offset_hours": 2.8,
                "duration": 145
            },
            {
                "customer": "Priya Sharma",
                "direction": CallDirection.INBOUND,
                "status": CallStatus.MISSED,
                "sid": "CA22222222222222222222222222222221",
                "offset_hours": 6,
                "duration": 0
            },
            {
                "customer": "Priya Sharma",
                "direction": CallDirection.OUTBOUND,
                "status": CallStatus.CALLBACK_INITIATED,
                "sid": "CA22222222222222222222222222222222",
                "offset_hours": 5.8,
                "duration": 45
            },
            {
                "customer": "Amit Patel",
                "direction": CallDirection.INBOUND,
                "status": CallStatus.MISSED,
                "sid": "CA33333333333333333333333333333331",
                "offset_hours": 24,
                "duration": 0
            },
            {
                "customer": "Sarah Jenkins",
                "direction": CallDirection.INBOUND,
                "status": CallStatus.ANSWERED,
                "sid": "CA44444444444444444444444444444441",
                "offset_hours": 48,
                "duration": 180
            },
        ]

        calls = {}
        for c_info in calls_data:
            result = await db.execute(select(Call).where(Call.twilio_call_sid == c_info["sid"]))
            call = result.scalar_one_or_none()
            if not call:
                cust = customers[c_info["customer"]]
                print(f"Creating call {c_info['sid']} for {cust.name}...")
                start = datetime.now(timezone.utc) - timedelta(hours=c_info["offset_hours"])
                call = Call(
                    business_id=business.id,
                    customer_id=cust.id,
                    twilio_call_sid=c_info["sid"],
                    direction=c_info["direction"],
                    status=c_info["status"],
                    from_number=cust.phone_number if c_info["direction"] == CallDirection.INBOUND else business.phone_number,
                    to_number=business.phone_number if c_info["direction"] == CallDirection.INBOUND else cust.phone_number,
                    duration_seconds=c_info["duration"],
                    started_at=start,
                    ended_at=start + timedelta(seconds=c_info["duration"]) if c_info["duration"] > 0 else None,
                )
                db.add(call)
                await db.flush()
            calls[c_info["sid"]] = call

        # 5. Create Conversations
        conversations_data = [
            {
                "customer": "Rajesh Kumar",
                "call_sid": "CA11111111111111111111111111111112",
                "channel": ConversationChannel.VOICE,
                "status": ConversationStatus.COMPLETED,
                "summary": "Needs urgent AC repair for office room because it is too hot.",
                "messages": [
                    {"role": "ai", "content": "Hello Rajesh, we noticed we missed your call. How can we help you today?", "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2.8)).isoformat()},
                    {"role": "customer", "content": "Hi, I need AC repair for my office. It stopped working and it is extremely hot.", "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2.8)).isoformat()},
                    {"role": "ai", "content": "I understand how uncomfortable that must be. When would you like our technician to visit?", "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2.78)).isoformat()},
                    {"role": "customer", "content": "Today if possible, tomorrow morning otherwise. First half of the day works best.", "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2.77)).isoformat()},
                    {"role": "ai", "content": "Noted. I've scheduled a technician visit for tomorrow 10 AM. Our coordinator will confirm details shortly.", "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2.76)).isoformat()}
                ],
                "offset_hours": 2.8
            },
            {
                "customer": "Priya Sharma",
                "call_sid": "CA22222222222222222222222222222222",
                "channel": ConversationChannel.WHATSAPP,
                "status": ConversationStatus.ACTIVE,
                "summary": "Kitchen sink pipe leakage causing flooding.",
                "messages": [
                    {"role": "ai", "content": "Hi Priya, you tried reaching us. How can we help with your plumbing?", "timestamp": (datetime.now(timezone.utc) - timedelta(hours=5.8)).isoformat()},
                    {"role": "customer", "content": "My kitchen sink pipe is leaking badly and there is water everywhere.", "timestamp": (datetime.now(timezone.utc) - timedelta(hours=5.79)).isoformat()},
                    {"role": "ai", "content": "That sounds very urgent. Our nearest plumber can visit today between 2-4 PM. Would that work for you?", "timestamp": (datetime.now(timezone.utc) - timedelta(hours=5.78)).isoformat()},
                    {"role": "customer", "content": "Yes that works. Please send someone as soon as possible.", "timestamp": (datetime.now(timezone.utc) - timedelta(hours=5.77)).isoformat()}
                ],
                "offset_hours": 5.8
            }
        ]

        conversations = {}
        for conv_info in conversations_data:
            cust = customers[conv_info["customer"]]
            call = calls.get(conv_info["call_sid"])
            result = await db.execute(
                select(Conversation).where(
                    Conversation.call_id == (call.id if call else None),
                    Conversation.customer_id == cust.id
                )
            )
            conv = result.scalar_one_or_none()
            if not conv:
                print(f"Creating conversation for {cust.name}...")
                start = datetime.now(timezone.utc) - timedelta(hours=conv_info["offset_hours"])
                conv = Conversation(
                    call_id=call.id if call else None,
                    customer_id=cust.id,
                    business_id=business.id,
                    channel=conv_info["channel"],
                    status=conv_info["status"],
                    messages=conv_info["messages"],
                    language="en",
                    ai_summary=conv_info["summary"],
                    started_at=start,
                    ended_at=start + timedelta(minutes=10) if conv_info["status"] == ConversationStatus.COMPLETED else None,
                )
                db.add(conv)
                await db.flush()
            conversations[conv_info["customer"]] = conv

        # 6. Create Leads
        leads_data = [
            {
                "customer": "Rajesh Kumar",
                "service": "AC Repair",
                "category": "hot",
                "score": 85,
                "urgency": "high",
                "intent": "service",
                "status": "qualified",
                "revenue": Decimal("4500.00"),
                "conv_customer": "Rajesh Kumar"
            },
            {
                "customer": "Priya Sharma",
                "service": "Plumbing Pipe Repair",
                "category": "hot",
                "score": 95,
                "urgency": "high",
                "intent": "service",
                "status": "contacted",
                "revenue": Decimal("2500.00"),
                "conv_customer": "Priya Sharma"
            },
            {
                "customer": "Amit Patel",
                "service": "General Plumbing inquiry",
                "category": "cold",
                "score": 25,
                "urgency": "low",
                "intent": "general",
                "status": "new",
                "revenue": Decimal("0.00"),
                "conv_customer": None
            }
        ]

        leads = {}
        for l_info in leads_data:
            cust = customers[l_info["customer"]]
            result = await db.execute(
                select(Lead).where(
                    Lead.customer_id == cust.id,
                    Lead.business_id == business.id
                )
            )
            lead = result.scalar_one_or_none()
            if not lead:
                print(f"Creating lead for {cust.name}...")
                conv = conversations.get(l_info["conv_customer"]) if l_info["conv_customer"] else None
                lead = Lead(
                    customer_id=cust.id,
                    business_id=business.id,
                    conversation_id=conv.id if conv else None,
                    service_requested=l_info["service"],
                    category=l_info["category"],
                    lead_score=l_info["score"],
                    urgency=l_info["urgency"],
                    purchase_readiness="ready" if l_info["category"] == "hot" else "browsing",
                    customer_intent=l_info["intent"],
                    status=l_info["status"],
                    estimated_revenue=l_info["revenue"],
                    currency="INR",
                    qualified_at=datetime.now(timezone.utc) - timedelta(hours=2) if l_info["status"] in ["qualified", "converted"] else None,
                )
                db.add(lead)
                await db.flush()
            leads[l_info["customer"]] = lead

        # 7. Create Revenue Predictions
        for name, lead in leads.items():
            if lead.estimated_revenue > 0:
                result = await db.execute(select(RevenuePrediction).where(RevenuePrediction.lead_id == lead.id))
                pred = result.scalar_one_or_none()
                if not pred:
                    print(f"Creating revenue prediction for lead {name}...")
                    pred = RevenuePrediction(
                        lead_id=lead.id,
                        business_id=business.id,
                        revenue_score=lead.lead_score,
                        estimated_revenue=lead.estimated_revenue,
                        currency="INR",
                        conversion_probability=0.85 if lead.lead_score > 80 else 0.50,
                        competitor_risk="low",
                        urgency=lead.urgency,
                        recommendation="Highly motivated customer. Proceed with dispatcher immediately." if lead.lead_score > 80 else "Regular follow up.",
                        scoring_factors={"sentiment": "neutral", "intent": "high"},
                        predicted_at=datetime.now(timezone.utc),
                    )
                    db.add(pred)
                    await db.flush()

        # 8. Create Appointments
        result = await db.execute(select(Appointment).where(Appointment.business_id == business.id))
        appts = result.scalars().all()
        if not appts:
            print("Creating appointment...")
            cust = customers["Rajesh Kumar"]
            lead = leads["Rajesh Kumar"]
            appt = Appointment(
                lead_id=lead.id,
                customer_id=cust.id,
                business_id=business.id,
                title="Office AC Repair Technician Visit",
                description="Technician to visit and troubleshoot office split AC unit not cooling.",
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=1, hours=3),  # tomorrow
                duration_minutes=60,
                status="confirmed",
                confirmation_sent_via="whatsapp",
                reminder_sent=False,
            )
            db.add(appt)
            await db.flush()

        # 9. Create Notifications
        result = await db.execute(select(Notification).where(Notification.user_id == user.id))
        notifs = result.scalars().all()
        if not notifs:
            print("Creating notifications...")
            notif_list = [
                Notification(
                    user_id=user.id,
                    business_id=business.id,
                    type="hot_lead",
                    title="New Hot Lead Detected!",
                    message="Rajesh Kumar requested urgent office AC repair. Call score: 85.",
                    channel="in_app",
                    is_read=False,
                    metadata_={},
                    sent_at=datetime.now(timezone.utc) - timedelta(hours=2.8),
                ),
                Notification(
                    user_id=user.id,
                    business_id=business.id,
                    type="appointment",
                    title="Appointment Booked",
                    message="AC repair technician visit confirmed for Rajesh Kumar tomorrow at 10 AM.",
                    channel="in_app",
                    is_read=False,
                    metadata_={},
                    sent_at=datetime.now(timezone.utc) - timedelta(hours=2.7),
                ),
                Notification(
                    user_id=user.id,
                    business_id=business.id,
                    type="missed_call",
                    title="Missed Call Received",
                    message="Missed call from Priya Sharma (+919876543211). Callback conversation started.",
                    channel="in_app",
                    is_read=True,
                    metadata_={},
                    sent_at=datetime.now(timezone.utc) - timedelta(hours=5.8),
                )
            ]
            db.add_all(notif_list)
            await db.flush()

        # Commit everything
        await db.commit()
        print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
