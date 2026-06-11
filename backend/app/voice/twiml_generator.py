"""CallRevive AI — TwiML XML response generator."""
from __future__ import annotations

from twilio.twiml.voice_response import VoiceResponse, Gather

from app.core.config import get_settings
from app.voice.language_config import get_language_config

settings = get_settings()


def generate_greeting(language: str = "en-in") -> str:
    """Generate TwiML greeting with speech gather."""
    lang_cfg = get_language_config(language)
    response = VoiceResponse()
    gather = Gather(
        input="speech", language=lang_cfg.twilio_locale,
        action=f"{settings.BACKEND_URL}/api/v1/webhooks/twilio/voice/gather",
        speech_timeout="auto", timeout=5,
    )
    gather.say(
        "Hello, we noticed we missed your call. How can we help you today?",
        voice=lang_cfg.voice_name, language=lang_cfg.twilio_locale,
    )
    response.append(gather)
    response.say("We didn't hear a response. Goodbye!", voice=lang_cfg.voice_name)
    return str(response)


def generate_response(text: str, language: str = "en-in") -> str:
    """Generate TwiML with AI response text."""
    lang_cfg = get_language_config(language)
    response = VoiceResponse()
    response.say(text, voice=lang_cfg.voice_name, language=lang_cfg.twilio_locale)
    return str(response)


def generate_gather(prompt_text: str, language: str = "en-in") -> str:
    """Generate TwiML gather for continued conversation."""
    lang_cfg = get_language_config(language)
    response = VoiceResponse()
    gather = Gather(
        input="speech", language=lang_cfg.twilio_locale,
        action=f"{settings.BACKEND_URL}/api/v1/webhooks/twilio/voice/gather",
        speech_timeout="auto",
    )
    gather.say(prompt_text, voice=lang_cfg.voice_name, language=lang_cfg.twilio_locale)
    response.append(gather)
    return str(response)


def generate_goodbye(language: str = "en-in") -> str:
    """Generate closing TwiML."""
    lang_cfg = get_language_config(language)
    response = VoiceResponse()
    response.say(
        "Thank you for your time. Our team will follow up with you shortly. Goodbye!",
        voice=lang_cfg.voice_name, language=lang_cfg.twilio_locale,
    )
    return str(response)
