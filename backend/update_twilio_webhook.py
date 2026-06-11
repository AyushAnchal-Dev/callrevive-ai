import os
from twilio.rest import Client
from app.core.config import get_settings

def update():
    settings = get_settings()
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    phone_number = settings.TWILIO_PHONE_NUMBER
    public_url = settings.BACKEND_URL

    if not account_sid or not auth_token or not phone_number:
        print("Missing Twilio credentials in environment.")
        return

    client = Client(account_sid, auth_token)
    webhook_url = f"{public_url}/api/v1/webhooks/twilio/voice"

    print(f"Searching for Twilio phone number {phone_number}...")
    numbers = client.incoming_phone_numbers.list(phone_number=phone_number)
    if not numbers:
        print(f"Phone number {phone_number} not found in Twilio account.")
        return

    number = numbers[0]
    print(f"Found phone number Sid: {number.sid}. Updating Voice Webhook to {webhook_url}...")
    client.incoming_phone_numbers(number.sid).update(
        voice_url=webhook_url,
        voice_method="POST"
    )
    print("Twilio phone number voice webhook updated successfully!")

if __name__ == "__main__":
    update()
