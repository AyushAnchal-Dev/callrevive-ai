from twilio.rest import Client
from app.core.config import get_settings

def query_account():
    settings = get_settings()
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN

    if not account_sid or not auth_token:
        print("Missing Twilio credentials in environment.")
        return

    client = Client(account_sid, auth_token)
    print("Fetching Twilio account details...")
    acc = client.api.accounts(account_sid).fetch()
    print(f"Account Name: {acc.friendly_name}")
    print(f"Account Status: {acc.status}")
    print(f"Account Type: {acc.type}")
    
    print("\nFetching Twilio usage records...")
    usage = client.usage.records.list(limit=5)
    for record in usage:
        print(f"Category: {record.category} | Description: {record.description} | Usage: {record.usage} {record.usage_unit} | Price: {record.price} {record.price_unit}")

if __name__ == "__main__":
    query_account()
