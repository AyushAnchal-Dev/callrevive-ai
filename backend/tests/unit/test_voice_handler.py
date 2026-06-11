import pytest
from unittest.mock import AsyncMock, patch, ANY
from app.voice.voice_handler import VoiceHandler
import app.worker.tasks.call_tasks  # Import explicitly so that unittest.mock can resolve the path attributes

@pytest.mark.asyncio
@patch("app.voice.voice_handler.Redis")
@patch("app.voice.voice_handler.get_gemini_client")
async def test_voice_handler_multi_turn(mock_get_gemini, mock_redis_class):
    # 1. Mock Redis client get/set operations
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None  # No prior history
    mock_redis_class.from_url.return_value = mock_redis

    # 2. Mock Gemini generative response containing [END]
    mock_gemini = AsyncMock()
    mock_gemini.generate.return_value = "I've noted your issue. Goodbye! [END]"
    mock_gemini.fast_model = "gemini-2.5-flash"
    mock_get_gemini.return_value = mock_gemini

    # Mock the Celery complete task delay dispatch
    with patch("app.worker.tasks.call_tasks.complete_voice_session.delay") as mock_task_delay:
        vh = VoiceHandler()
        
        # Call under test
        twiml_response = await vh.handle_speech_input(
            speech_text="My pipe is leaking in the kitchen.",
            call_sid="test-call-sid-123",
            language="en-IN"
        )

        # 3. Asserts
        assert "<Response>" in twiml_response
        assert "Goodbye" in twiml_response
        
        # Verify Redis gets history
        mock_redis.get.assert_called_once_with("call:session:test-call-sid-123")
        # Verify history gets updated and saved
        mock_redis.set.assert_called_once()
        
        # Verify Celery delay triggered for post-call summaries
        mock_task_delay.assert_called_once_with("test-call-sid-123", ANY)
