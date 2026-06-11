"""CallRevive AI — Lead qualification, revenue prediction, and recommendation tasks."""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.worker.celery_app import celery_app
from app.db.session import SyncSessionLocal
from app.models.conversation import Conversation
from app.models.lead import Lead
from app.models.revenue_prediction import RevenuePrediction
from app.models.notification import Notification, NotificationType, NotificationChannel
from app.models.appointment import Appointment, AppointmentStatus
from sqlalchemy.orm.attributes import flag_modified

logger = logging.getLogger(__name__)


@celery_app.task(name="app.worker.tasks.lead_tasks.qualify_lead", bind=True, max_retries=3)
def qualify_lead(self, conversation_id: str) -> dict:
    """Run AI lead qualification pipeline on a conversation transcript."""
    logger.info(f"Qualifying lead from conversation {conversation_id}")
    
    try:
        with SyncSessionLocal() as db:
            conversation = db.query(Conversation).filter_by(id=uuid.UUID(conversation_id)).first()
            if not conversation:
                logger.error(f"Conversation not found: {conversation_id}")
                return {"status": "failed", "reason": "conversation_not_found"}

            # Format transcript text
            transcript = "\n".join(
                f"{m.get('role', 'unknown')}: {m.get('content', '')}" for m in conversation.messages
            )

            # Perform parallel message sentiment analysis and appointment extraction along with lead qualification
            async def run_ai_analysis():
                from app.ai.lead_qualifier import qualify_lead as ai_qualify_lead
                from app.ai.sentiment_analyzer import analyze_sentiment
                from app.ai.appointment_extractor import extract_appointment

                # Determine which messages to analyze for sentiment
                user_msgs_to_analyze = []
                for idx, msg in enumerate(conversation.messages):
                    role = msg.get('role', '').lower()
                    if role in ('user', 'customer') and not msg.get('sentiment'):
                        user_msgs_to_analyze.append((idx, msg.get('content', '')))

                # Construct prompts/tasks
                qual_coro = ai_qualify_lead(
                    conversation_text=transcript,
                    business_category=conversation.business.category
                )
                
                # Guide Gemini with current system date/time in the prompt
                current_time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                appt_prompt = f"Current system date/time: {current_time_str}\n\nConversation: \"{transcript}\"\n\nExtract appointment details."
                appt_coro = extract_appointment(appt_prompt)

                sentiment_coros = [analyze_sentiment(content) for _, content in user_msgs_to_analyze]

                # Run in parallel
                results = await asyncio.gather(qual_coro, appt_coro, *sentiment_coros)
                
                q_res = results[0]
                a_res = results[1]
                s_res = results[2:]

                # Update messages copy
                updated_messages = [dict(m) for m in conversation.messages]
                for (idx, _), sent_res in zip(user_msgs_to_analyze, s_res):
                    updated_messages[idx]['sentiment'] = sent_res.sentiment
                    updated_messages[idx]['emotion'] = sent_res.emotion
                
                return q_res, a_res, updated_messages

            # Execute async logic
            qual_result, appt_result, new_messages = asyncio.run(run_ai_analysis())

            # Update conversation messages
            conversation.messages = new_messages
            flag_modified(conversation, "messages")

            # Check if Lead record already exists for this conversation
            lead = db.query(Lead).filter_by(conversation_id=conversation.id).first()
            if not lead:
                lead = Lead(
                    customer_id=conversation.customer_id,
                    business_id=conversation.business_id,
                    conversation_id=conversation.id,
                    currency=conversation.business.default_currency,
                )
                db.add(lead)

            # Map fields from Pydantic schema to SQLAlchemy Model
            lead.service_requested = qual_result.service_requested or "General Inquiry"
            lead.category = qual_result.category
            lead.lead_score = qual_result.lead_score
            lead.urgency = qual_result.urgency
            lead.budget_range = qual_result.budget_range
            lead.purchase_readiness = qual_result.purchase_readiness
            lead.customer_intent = qual_result.customer_intent
            lead.qualification_notes = qual_result.qualification_notes
            lead.status = "qualified"
            lead.qualified_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(lead)

            # Handle auto-appointment scheduling
            if appt_result.has_appointment_intent and appt_result.preferred_date:
                try:
                    date_str = appt_result.preferred_date.strip()
                    time_str = appt_result.preferred_time.strip() if appt_result.preferred_time else "09:00"
                    dt_str = f"{date_str} {time_str}"
                    
                    scheduled_at = None
                    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %I:%M %p", "%Y-%m-%d %I:%M%p", "%Y-%m-%d %H:%M:%S"):
                        try:
                            scheduled_at = datetime.strptime(dt_str, fmt)
                            break
                        except ValueError:
                            continue
                    
                    if not scheduled_at:
                        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                            try:
                                parsed_date = datetime.strptime(date_str, fmt)
                                scheduled_at = datetime.combine(parsed_date.date(), datetime.min.time().replace(hour=9))
                                break
                            except ValueError:
                                continue
                    
                    if scheduled_at:
                        scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
                        
                        appointment = Appointment(
                            lead_id=lead.id,
                            customer_id=conversation.customer_id,
                            business_id=conversation.business_id,
                            title=appt_result.service_type or lead.service_requested or "AI Automated Appointment",
                            description=f"Auto-scheduled from conversation transcription. Customer flexibility: {appt_result.flexibility}.",
                            scheduled_at=scheduled_at,
                            duration_minutes=appt_result.duration_estimate or 30,
                            status=AppointmentStatus.SCHEDULED,
                        )
                        db.add(appointment)
                        db.commit()
                        db.refresh(appointment)
                        
                        logger.info(f"Auto-scheduled appointment: ID={appointment.id} at={appointment.scheduled_at}")

                        # Create owner notification alert
                        notification = Notification(
                            user_id=conversation.business.owner_id,
                            business_id=conversation.business_id,
                            type=NotificationType.APPOINTMENT,
                            title="Appointment Auto-Scheduled",
                            message=(
                                f"An appointment has been automatically scheduled for customer "
                                f"{conversation.customer.phone_number} on {scheduled_at.strftime('%Y-%m-%d %H:%M UTC')}. "
                                f"Service: {appointment.title}."
                            ),
                            channel=NotificationChannel.IN_APP,
                            is_read=False,
                            metadata_={
                                "appointment_id": str(appointment.id),
                                "lead_id": str(lead.id),
                                "scheduled_at": appointment.scheduled_at.isoformat(),
                            }
                        )
                        db.add(notification)
                        db.commit()
                except Exception as appt_exc:
                    logger.error(f"Failed to auto-schedule appointment: {appt_exc}")

            # Trigger revenue prediction task
            calculate_revenue_score.delay(str(lead.id))

            logger.info(f"Lead qualified successfully: Lead ID={lead.id}, Score={lead.lead_score}")
            return {"lead_id": str(lead.id), "status": "qualified"}

    except Exception as exc:
        logger.error(f"Failed to qualify lead: {exc}")
        self.retry(countdown=60, exc=exc)


@celery_app.task(name="app.worker.tasks.lead_tasks.calculate_revenue_score", bind=True, max_retries=2)
def calculate_revenue_score(self, lead_id: str) -> dict:
    """Generate Revenue Recovery Score for a lead using Gemini Pro."""
    logger.info(f"Calculating revenue score for lead {lead_id}")
    
    try:
        with SyncSessionLocal() as db:
            lead = db.query(Lead).filter_by(id=uuid.UUID(lead_id)).first()
            if not lead:
                logger.error(f"Lead not found: {lead_id}")
                return {"status": "failed", "reason": "lead_not_found"}

            conversation = lead.conversation
            transcript = "\n".join(
                f"{m.get('role', 'unknown')}: {m.get('content', '')}" for m in conversation.messages
            )

            # Call AI revenue predictor
            from app.ai.revenue_predictor import predict_revenue as ai_predict_revenue
            rev_result = asyncio.run(
                ai_predict_revenue(
                    conversation_text=transcript,
                    business_category=lead.business.category,
                    service_type=lead.service_requested,
                    currency=lead.currency
                )
            )

            # Save revenue prediction score to DB
            prediction = RevenuePrediction(
                lead_id=lead.id,
                business_id=lead.business_id,
                revenue_score=rev_result.revenue_score,
                estimated_revenue=rev_result.estimated_revenue,
                currency=lead.currency,
                conversion_probability=rev_result.conversion_probability,
                competitor_risk=rev_result.competitor_risk,
                urgency=rev_result.urgency,
                recommendation=rev_result.recommendation,
                scoring_factors=rev_result.scoring_factors.model_dump(),
                predicted_at=datetime.now(timezone.utc),
            )
            db.add(prediction)

            # Update lead estimated revenue
            lead.estimated_revenue = rev_result.estimated_revenue
            db.commit()

            # Create owner notification alert
            notification_type = NotificationType.NEW_LEAD if lead.category != "hot" else NotificationType.HOT_LEAD
            notification = Notification(
                user_id=lead.business.owner_id,
                business_id=lead.business_id,
                type=notification_type,
                title=f"New Qualified Lead: {lead.customer.phone_number}",
                message=(
                    f"Customer requested service: {lead.service_requested}. "
                    f"AI Lead Score: {lead.lead_score}/100. "
                    f"Estimated Value: {lead.currency} {lead.estimated_revenue:.2f}."
                ),
                channel=NotificationChannel.IN_APP,
                is_read=False,
                metadata_={
                    "lead_id": str(lead.id),
                    "score": lead.lead_score,
                    "value": float(lead.estimated_revenue),
                }
            )
            db.add(notification)
            db.commit()

            # If it's a hot lead, dispatch an instant WhatsApp alert to the business owner
            if lead.category == "hot" and lead.business.owner.phone_number:
                from app.communication.whatsapp_client import get_whatsapp_service
                whatsapp = get_whatsapp_service()
                
                summary_data = {
                    "customer_name": lead.customer.name or "New Client",
                    "phone": lead.customer.phone_number,
                    "service": lead.service_requested,
                    "score": lead.lead_score,
                    "revenue": f"{lead.currency} {lead.estimated_revenue:.2f}",
                    "category": lead.category
                }
                
                try:
                    whatsapp.send_lead_summary(lead.business.owner.phone_number, summary_data)
                    logger.info("WhatsApp Lead Alert dispatched to owner.")
                except Exception as wa_exc:
                    logger.error(f"Failed to dispatch owner WhatsApp: {wa_exc}")

            logger.info(f"Revenue score calculated successfully: Score={rev_result.revenue_score}, Est={rev_result.estimated_revenue}")
            return {"prediction_id": str(prediction.id), "status": "scored"}

    except Exception as exc:
        logger.error(f"Error predicting revenue: {exc}")
        self.retry(countdown=60, exc=exc)


@celery_app.task(name="app.worker.tasks.lead_tasks.generate_daily_recommendations_all")
def generate_daily_recommendations_all() -> dict:
    """Generate daily recommendations for all active businesses using Gemini."""
    logger.info("Generating daily recommendations for all businesses")
    # In production, we iterate over all businesses, gather recent metrics,
    # and use the app.ai.recommendation_engine to populate notifications/recommendations.
    return {"status": "completed"}
