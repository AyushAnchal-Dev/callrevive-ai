from twilio.rest import Client
from app.core.config import get_settings

def query_twilio():
    settings = get_settings()
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN

    if not account_sid or not auth_token:
        print("Missing Twilio credentials in environment.")
        return

    client = Client(account_sid, auth_token)
    print("Fetching ALL recent calls in Twilio account...")
    
    calls = client.calls.list(limit=20)
    if not calls:
        print("No calls found in the entire Twilio account.")
    for c in calls:
        print(f"Call SID: {c.sid} | From: {c.from_} | To: {c.to} | Status: {c.status} | Direction: {c.direction} | Start: {c.start_time}")

if __name__ == "__main__":
    query_twilio()
