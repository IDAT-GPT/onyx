"""Open-source / self-hosted voice provider (OpenAI-compatible API).

Works with any speech server that exposes the OpenAI audio endpoints:

- STT: ``POST {base}/v1/audio/transcriptions`` (e.g. Speaches / faster-whisper,
  whisper.cpp server, LocalAI)
- TTS: ``POST {base}/v1/audio/speech`` (e.g. Speaches / Kokoro, Kokoro-FastAPI,
  openedai-speech / Piper)

Recommended stack: one Speaches container (https://speaches.ai) serving both
faster-whisper (STT) and Kokoro-82M (TTS).

Deployment defaults live in the constants below — edit them, or set the
matching environment variables, to hard-wire your speech stack in code. The
admin Voice page can override all of them per provider.
"""

import os
from typing import Any

from onyx.voice.providers.openai import OpenAIVoiceProvider

# ---------------------------------------------------------------------------
# Code-level defaults (environment variables override; admin UI overrides both)
# ---------------------------------------------------------------------------
CUSTOM_SPEECH_API_BASE = os.environ.get("CUSTOM_SPEECH_API_BASE", "")
CUSTOM_SPEECH_API_KEY = os.environ.get("CUSTOM_SPEECH_API_KEY", "")
CUSTOM_SPEECH_STT_MODEL = os.environ.get(
    "CUSTOM_SPEECH_STT_MODEL", "Systran/faster-whisper-large-v3"
)
CUSTOM_SPEECH_TTS_MODEL = os.environ.get(
    "CUSTOM_SPEECH_TTS_MODEL", "speaches-ai/Kokoro-82M-v1.0-ONNX"
)
CUSTOM_SPEECH_TTS_VOICE = os.environ.get("CUSTOM_SPEECH_TTS_VOICE", "af_heart")

# Self-hosted servers usually run without auth, but the OpenAI client requires
# a non-empty key — send a placeholder the server ignores.
PLACEHOLDER_API_KEY = "not-needed"

CUSTOM_STT_MODELS = [
    {"id": "Systran/faster-whisper-large-v3", "name": "Faster-Whisper Large v3"},
    {
        "id": "deepdml/faster-whisper-large-v3-turbo-ct2",
        "name": "Faster-Whisper Large v3 Turbo",
    },
    {"id": "Systran/faster-whisper-medium", "name": "Faster-Whisper Medium"},
    {"id": "Systran/faster-whisper-small", "name": "Faster-Whisper Small"},
]

CUSTOM_TTS_MODELS = [
    {"id": "speaches-ai/Kokoro-82M-v1.0-ONNX", "name": "Kokoro 82M"},
]

# Kokoro voice ids (a=American, b=British; f=female, m=male).
KOKORO_VOICES = [
    {"id": "af_heart", "name": "Heart (US female)"},
    {"id": "af_bella", "name": "Bella (US female)"},
    {"id": "af_nicole", "name": "Nicole (US female)"},
    {"id": "af_sarah", "name": "Sarah (US female)"},
    {"id": "am_adam", "name": "Adam (US male)"},
    {"id": "am_michael", "name": "Michael (US male)"},
    {"id": "bf_emma", "name": "Emma (UK female)"},
    {"id": "bf_isabella", "name": "Isabella (UK female)"},
    {"id": "bm_george", "name": "George (UK male)"},
    {"id": "bm_lewis", "name": "Lewis (UK male)"},
]


def _normalize_api_base(api_base: str | None) -> str | None:
    """Canonical form has no trailing slash and no `/v1` suffix.

    The OpenAI SDK client gets `/v1` appended in `_get_client`; the streaming
    synthesizer inherited from the OpenAI provider appends `/v1` itself.
    """
    base = (api_base or "").strip().rstrip("/")
    if base.endswith("/v1"):
        base = base[: -len("/v1")].rstrip("/")
    return base or None


class CustomVoiceProvider(OpenAIVoiceProvider):
    """Self-hosted, OpenAI-compatible STT/TTS server (Speaches, Kokoro, ...)."""

    def __init__(
        self,
        api_key: str | None,
        api_base: str | None = None,
        stt_model: str | None = None,
        tts_model: str | None = None,
        default_voice: str | None = None,
        custom_config: dict[str, Any] | None = None,
    ):
        super().__init__(
            api_key=api_key or CUSTOM_SPEECH_API_KEY or PLACEHOLDER_API_KEY,
            api_base=_normalize_api_base(api_base or CUSTOM_SPEECH_API_BASE),
            stt_model=stt_model or CUSTOM_SPEECH_STT_MODEL,
            tts_model=tts_model or CUSTOM_SPEECH_TTS_MODEL,
            default_voice=default_voice or CUSTOM_SPEECH_TTS_VOICE,
        )
        self.custom_config = custom_config or {}

    def _get_client(self) -> Any:
        if self._client is None:
            if not self.api_base:
                raise ValueError(
                    "The open-source speech provider needs a server URL "
                    "(Target URI), e.g. http://host.docker.internal:8000."
                )
            from openai import AsyncOpenAI

            # The OpenAI SDK expects the base URL to include /v1.
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=f"{self.api_base}/v1",
            )
        return self._client

    async def validate_credentials(self) -> None:
        """Validate by listing models — supported by OpenAI-compatible servers."""
        if not self.api_base:
            raise RuntimeError(
                "Server URL (Target URI) is required for the open-source "
                "speech provider."
            )
        client = self._get_client()
        try:
            await client.models.list()
        except Exception as e:
            raise RuntimeError(
                f"Could not reach the speech server at {self.api_base}: {e}"
            ) from e

    def get_available_voices(self) -> list[dict[str, str]]:
        """Voices from custom_config["voices"] when set, else Kokoro defaults.

        custom_config["voices"] accepts a list of voice ids (strings) or
        {"id": ..., "name": ...} dictionaries.
        """
        configured = self.custom_config.get("voices")
        if isinstance(configured, list) and configured:
            voices: list[dict[str, str]] = []
            for entry in configured:
                if isinstance(entry, str):
                    voices.append({"id": entry, "name": entry})
                elif isinstance(entry, dict) and "id" in entry:
                    voices.append(
                        {
                            "id": str(entry["id"]),
                            "name": str(entry.get("name", entry["id"])),
                        }
                    )
            if voices:
                return voices
        return KOKORO_VOICES.copy()

    def get_available_stt_models(self) -> list[dict[str, str]]:
        models = CUSTOM_STT_MODELS.copy()
        if self.stt_model and all(m["id"] != self.stt_model for m in models):
            models.insert(0, {"id": self.stt_model, "name": self.stt_model})
        return models

    def get_available_tts_models(self) -> list[dict[str, str]]:
        models = CUSTOM_TTS_MODELS.copy()
        if self.tts_model and all(m["id"] != self.tts_model for m in models):
            models.insert(0, {"id": self.tts_model, "name": self.tts_model})
        return models

    def supports_streaming_stt(self) -> bool:
        # Open-source servers have no OpenAI Realtime WebSocket; the caller
        # falls back to the chunked HTTP transcription path.
        return False

    def supports_streaming_tts(self) -> bool:
        # Inherited streaming TTS is plain HTTP against /v1/audio/speech,
        # which OpenAI-compatible servers support.
        return True

    async def create_streaming_transcriber(  # ty: ignore[invalid-method-override]
        self, _audio_format: str = "webm"
    ) -> Any:
        raise NotImplementedError(
            "Streaming STT is not supported by the open-source speech provider."
        )
