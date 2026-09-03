from onyx.db.models import VoiceProvider
from onyx.voice.factory import (
    get_voice_provider,
    voice_provider_has_credentials,
    voice_provider_requires_api_key,
)
from onyx.voice.providers.custom import (
    CUSTOM_SPEECH_STT_MODEL,
    CUSTOM_SPEECH_TTS_MODEL,
    CUSTOM_SPEECH_TTS_VOICE,
    KOKORO_VOICES,
    PLACEHOLDER_API_KEY,
    CustomVoiceProvider,
)


def _temp_provider(**overrides: object) -> VoiceProvider:
    provider = VoiceProvider(name="__test__", provider_type="custom")
    provider.api_base = overrides.get("api_base", "http://localhost:8000")  # type: ignore[assignment]
    for key, value in overrides.items():
        setattr(provider, key, value)
    return provider


def test_factory_dispatches_custom_provider() -> None:
    provider = get_voice_provider(_temp_provider())
    assert isinstance(provider, CustomVoiceProvider)


def test_keyless_provider_gets_placeholder_key_and_code_defaults() -> None:
    provider = get_voice_provider(_temp_provider())
    assert isinstance(provider, CustomVoiceProvider)
    assert provider.api_key == PLACEHOLDER_API_KEY
    assert provider.stt_model == CUSTOM_SPEECH_STT_MODEL
    assert provider.tts_model == CUSTOM_SPEECH_TTS_MODEL
    assert provider.default_voice == CUSTOM_SPEECH_TTS_VOICE


def test_api_base_normalization_strips_v1_suffix() -> None:
    provider = CustomVoiceProvider(
        api_key=None, api_base="http://speech.local:8000/v1/"
    )
    assert provider.api_base == "http://speech.local:8000"


def test_voices_default_to_kokoro_and_respect_custom_config() -> None:
    default_provider = CustomVoiceProvider(api_key=None, api_base="http://x")
    assert default_provider.get_available_voices() == KOKORO_VOICES

    configured = CustomVoiceProvider(
        api_key=None,
        api_base="http://x",
        custom_config={"voices": ["nova", {"id": "vega", "name": "Vega"}]},
    )
    assert configured.get_available_voices() == [
        {"id": "nova", "name": "nova"},
        {"id": "vega", "name": "Vega"},
    ]


def test_configured_models_appear_in_model_lists() -> None:
    provider = CustomVoiceProvider(
        api_key=None,
        api_base="http://x",
        stt_model="my-org/my-whisper",
        tts_model="my-org/my-tts",
    )
    assert provider.get_available_stt_models()[0] == {
        "id": "my-org/my-whisper",
        "name": "my-org/my-whisper",
    }
    assert provider.get_available_tts_models()[0] == {
        "id": "my-org/my-tts",
        "name": "my-org/my-tts",
    }


def test_streaming_capabilities() -> None:
    provider = CustomVoiceProvider(api_key=None, api_base="http://x")
    assert provider.supports_streaming_stt() is False
    assert provider.supports_streaming_tts() is True


def test_api_key_requirement_by_provider_type() -> None:
    assert voice_provider_requires_api_key("custom") is False
    assert voice_provider_requires_api_key("openai") is True
    assert voice_provider_requires_api_key("azure") is True

    keyless_custom = _temp_provider()
    assert voice_provider_has_credentials(keyless_custom) is True

    keyless_openai = VoiceProvider(name="__test2__", provider_type="openai")
    assert voice_provider_has_credentials(keyless_openai) is False
