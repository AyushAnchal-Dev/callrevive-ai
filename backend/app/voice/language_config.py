"""CallRevive AI — Multi-language voice configuration."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LanguageConfig:
    code: str
    twilio_locale: str
    voice_name: str
    display_name: str


SUPPORTED_LANGUAGES: dict[str, LanguageConfig] = {
    "en": LanguageConfig("en", "en-US", "Polly.Joanna", "English"),
    "en-in": LanguageConfig("en-in", "en-IN", "Polly.Aditi", "English (India)"),
    "hi": LanguageConfig("hi", "hi-IN", "Polly.Aditi", "Hindi"),
    "ta": LanguageConfig("ta", "ta-IN", "Polly.Aditi", "Tamil"),
    "te": LanguageConfig("te", "te-IN", "Polly.Aditi", "Telugu"),
    "kn": LanguageConfig("kn", "kn-IN", "Polly.Aditi", "Kannada"),
    "ml": LanguageConfig("ml", "ml-IN", "Polly.Aditi", "Malayalam"),
    "bn": LanguageConfig("bn", "bn-IN", "Polly.Aditi", "Bengali"),
    "gu": LanguageConfig("gu", "gu-IN", "Polly.Aditi", "Gujarati"),
    "mr": LanguageConfig("mr", "mr-IN", "Polly.Aditi", "Marathi"),
    "pa": LanguageConfig("pa", "pa-IN", "Polly.Aditi", "Punjabi"),
    "ur": LanguageConfig("ur", "ur-IN", "Polly.Aditi", "Urdu"),
}

DEFAULT_LANGUAGE = "en-in"


def get_language_config(language_code: str) -> LanguageConfig:
    """Get language configuration, falling back to default."""
    return SUPPORTED_LANGUAGES.get(language_code, SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE])
