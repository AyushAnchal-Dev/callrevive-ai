import pytest
from unittest.mock import patch
from httpx import AsyncClient

@pytest.mark.asyncio
@patch("app.worker.tasks.call_tasks.process_missed_call.delay")
async def test_twilio_voice_webhook_missed_call(mock_process_missed, client: AsyncClient):
    # Test missed call (busy / no-answer status) triggers process_missed_call task
    payload = {
        "CallStatus": "busy",
        "CallSid": "CA1234567890abcdef",
        "From": "+1234567890",
        "To": "+1098765432"
    }
    response = await client.post(
        "/api/v1/webhooks/twilio/voice",
        data=payload
    )
    assert response.status_code == 200
    assert "application/xml" in response.headers["content-type"]
    assert "<Response>" in response.text
    
    mock_process_missed.assert_called_once_with({
        "call_sid": "CA1234567890abcdef",
        "from": "+1234567890",
        "to": "+1098765432"
    })

@pytest.mark.asyncio
async def test_twilio_voice_webhook_ringing(client: AsyncClient):
    # Test ringing status returns immediate greeting and hangup response
    payload = {
        "CallStatus": "ringing",
        "CallSid": "CA1234567890abcdef",
        "From": "+1234567890",
        "To": "+1098765432"
    }
    response = await client.post(
        "/api/v1/webhooks/twilio/voice",
        data=payload
    )
    assert response.status_code == 200
    assert "application/xml" in response.headers["content-type"]
    assert "<Hangup />" in response.text
    assert "unable to answer right now" in response.text

@pytest.mark.asyncio
@patch("app.voice.voice_handler.VoiceHandler.handle_speech_input")
async def test_twilio_voice_gather_with_speech(mock_handle_speech, client: AsyncClient):
    # Test voice gather with speech result delegates to VoiceHandler
    mock_handle_speech.return_value = "<Response><Say>Mock Speech Response</Say></Response>"
    payload = {
        "SpeechResult": "Hello, I want to book a room",
        "CallSid": "CA999888777",
        "language": "en-US"
    }
    response = await client.post(
        "/api/v1/webhooks/twilio/voice/gather",
        data=payload
    )
    assert response.status_code == 200
    assert "application/xml" in response.headers["content-type"]
    assert "Mock Speech Response" in response.text
    mock_handle_speech.assert_called_once_with("Hello, I want to book a room", "CA999888777", "en-US")

@pytest.mark.asyncio
async def test_twilio_voice_gather_no_speech(client: AsyncClient):
    # Test voice gather with no speech result asks to repeat
    payload = {
        "SpeechResult": "",
        "CallSid": "CA999888777",
        "language": "en-US"
    }
    response = await client.post(
        "/api/v1/webhooks/twilio/voice/gather",
        data=payload
    )
    assert response.status_code == 200
    assert "application/xml" in response.headers["content-type"]
    assert "I didn't catch that" in response.text

@pytest.mark.asyncio
@patch("app.worker.tasks.whatsapp_tasks.process_whatsapp_message.delay")
async def test_twilio_whatsapp_webhook(mock_process_whatsapp, client: AsyncClient):
    # Test WhatsApp webhook schedules process_whatsapp_message
    payload = {
        "From": "whatsapp:+1234567890",
        "Body": "Can you check my appointment?",
        "MessageSid": "SM12345"
    }
    response = await client.post(
        "/api/v1/webhooks/twilio/whatsapp",
        data=payload
    )
    assert response.status_code == 200
    assert "application/xml" in response.headers["content-type"]
    assert "<Response></Response>" in response.text
    mock_process_whatsapp.assert_called_once_with("+1234567890", "Can you check my appointment?")

@pytest.mark.asyncio
@patch("app.worker.tasks.call_tasks.store_recording.delay")
async def test_twilio_recording_webhook(mock_store_recording, client: AsyncClient):
    # Test recording completed webhook schedules store_recording
    payload = {
        "RecordingSid": "RE777777777",
        "RecordingUrl": "https://api.twilio.com/recording",
        "CallSid": "CA12345",
        "RecordingStatus": "completed"
    }
    response = await client.post(
        "/api/v1/webhooks/twilio/recording",
        data=payload
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_store_recording.assert_called_once_with("RE777777777", "https://api.twilio.com/recording", "CA12345")
