from twilio.rest import Client
from app.core.config import get_settings

def query_alerts():
    settings = get_settings()
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN

    if not account_sid or not auth_token:
        print("Missing Twilio credentials in environment.")
        return

    client = Client(account_sid, auth_token)
    print("Fetching recent Twilio Monitor Alerts...")
    
    alerts = client.monitor.alerts.list(limit=10)
    if not alerts:
        print("No alerts found in the Twilio account.")
    for alert in alerts:
        print(f"Alert SID: {alert.sid} | Log Level: {alert.log_level} | Error Code: {alert.error_code} | Date: {alert.alert_text} | Resource SID: {alert.resource_sid}")

if __name__ == "__main__":
    query_alerts()
