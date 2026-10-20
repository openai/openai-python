# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .audio import (
        Audio as Audio,
        AsyncAudio as AsyncAudio,
        AudioWithRawResponse as AudioWithRawResponse,
        AsyncAudioWithRawResponse as AsyncAudioWithRawResponse,
        AudioWithStreamingResponse as AudioWithStreamingResponse,
        AsyncAudioWithStreamingResponse as AsyncAudioWithStreamingResponse,
    )
    from .speech import (
        Speech as Speech,
        AsyncSpeech as AsyncSpeech,
        SpeechWithRawResponse as SpeechWithRawResponse,
        AsyncSpeechWithRawResponse as AsyncSpeechWithRawResponse,
        SpeechWithStreamingResponse as SpeechWithStreamingResponse,
        AsyncSpeechWithStreamingResponse as AsyncSpeechWithStreamingResponse,
    )
    from .voices import (
        Voices as Voices,
        AsyncVoices as AsyncVoices,
        VoicesWithRawResponse as VoicesWithRawResponse,
        AsyncVoicesWithRawResponse as AsyncVoicesWithRawResponse,
        VoicesWithStreamingResponse as VoicesWithStreamingResponse,
        AsyncVoicesWithStreamingResponse as AsyncVoicesWithStreamingResponse,
    )
    from .translations import (
        Translations as Translations,
        AsyncTranslations as AsyncTranslations,
        TranslationsWithRawResponse as TranslationsWithRawResponse,
        AsyncTranslationsWithRawResponse as AsyncTranslationsWithRawResponse,
        TranslationsWithStreamingResponse as TranslationsWithStreamingResponse,
        AsyncTranslationsWithStreamingResponse as AsyncTranslationsWithStreamingResponse,
    )
    from .transcriptions import (
        Transcriptions as Transcriptions,
        AsyncTranscriptions as AsyncTranscriptions,
        TranscriptionsWithRawResponse as TranscriptionsWithRawResponse,
        AsyncTranscriptionsWithRawResponse as AsyncTranscriptionsWithRawResponse,
        TranscriptionsWithStreamingResponse as TranscriptionsWithStreamingResponse,
        AsyncTranscriptionsWithStreamingResponse as AsyncTranscriptionsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Transcriptions": (".transcriptions", "Transcriptions"),
        "AsyncTranscriptions": (".transcriptions", "AsyncTranscriptions"),
        "TranscriptionsWithRawResponse": (".transcriptions", "TranscriptionsWithRawResponse"),
        "AsyncTranscriptionsWithRawResponse": (".transcriptions", "AsyncTranscriptionsWithRawResponse"),
        "TranscriptionsWithStreamingResponse": (".transcriptions", "TranscriptionsWithStreamingResponse"),
        "AsyncTranscriptionsWithStreamingResponse": (".transcriptions", "AsyncTranscriptionsWithStreamingResponse"),
        "Translations": (".translations", "Translations"),
        "AsyncTranslations": (".translations", "AsyncTranslations"),
        "TranslationsWithRawResponse": (".translations", "TranslationsWithRawResponse"),
        "AsyncTranslationsWithRawResponse": (".translations", "AsyncTranslationsWithRawResponse"),
        "TranslationsWithStreamingResponse": (".translations", "TranslationsWithStreamingResponse"),
        "AsyncTranslationsWithStreamingResponse": (".translations", "AsyncTranslationsWithStreamingResponse"),
        "Speech": (".speech", "Speech"),
        "AsyncSpeech": (".speech", "AsyncSpeech"),
        "SpeechWithRawResponse": (".speech", "SpeechWithRawResponse"),
        "AsyncSpeechWithRawResponse": (".speech", "AsyncSpeechWithRawResponse"),
        "SpeechWithStreamingResponse": (".speech", "SpeechWithStreamingResponse"),
        "AsyncSpeechWithStreamingResponse": (".speech", "AsyncSpeechWithStreamingResponse"),
        "Voices": (".voices", "Voices"),
        "AsyncVoices": (".voices", "AsyncVoices"),
        "VoicesWithRawResponse": (".voices", "VoicesWithRawResponse"),
        "AsyncVoicesWithRawResponse": (".voices", "AsyncVoicesWithRawResponse"),
        "VoicesWithStreamingResponse": (".voices", "VoicesWithStreamingResponse"),
        "AsyncVoicesWithStreamingResponse": (".voices", "AsyncVoicesWithStreamingResponse"),
        "Audio": (".audio", "Audio"),
        "AsyncAudio": (".audio", "AsyncAudio"),
        "AudioWithRawResponse": (".audio", "AudioWithRawResponse"),
        "AsyncAudioWithRawResponse": (".audio", "AsyncAudioWithRawResponse"),
        "AudioWithStreamingResponse": (".audio", "AudioWithStreamingResponse"),
        "AsyncAudioWithStreamingResponse": (".audio", "AsyncAudioWithStreamingResponse"),
    }
    _SUBMODULES = {
        "audio",
        "speech",
        "transcriptions",
        "translations",
        "voices",
    }

    def __getattr__(name: str) -> _t.Any:
        import importlib

        if name in _EXPORTS:
            module_name, symbol_name = _EXPORTS[name]
            value = getattr(importlib.import_module(module_name, __name__), symbol_name)
        elif name in _SUBMODULES:
            value = importlib.import_module(f".{name}", __name__)
        else:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
        globals()[name] = value
        return value

    def __dir__() -> list[str]:
        return sorted(set(globals()) | set(_EXPORTS) | _SUBMODULES)


__all__ = [
    "Transcriptions",
    "AsyncTranscriptions",
    "TranscriptionsWithRawResponse",
    "AsyncTranscriptionsWithRawResponse",
    "TranscriptionsWithStreamingResponse",
    "AsyncTranscriptionsWithStreamingResponse",
    "Translations",
    "AsyncTranslations",
    "TranslationsWithRawResponse",
    "AsyncTranslationsWithRawResponse",
    "TranslationsWithStreamingResponse",
    "AsyncTranslationsWithStreamingResponse",
    "Speech",
    "AsyncSpeech",
    "SpeechWithRawResponse",
    "AsyncSpeechWithRawResponse",
    "SpeechWithStreamingResponse",
    "AsyncSpeechWithStreamingResponse",
    "Voices",
    "AsyncVoices",
    "VoicesWithRawResponse",
    "AsyncVoicesWithRawResponse",
    "VoicesWithStreamingResponse",
    "AsyncVoicesWithStreamingResponse",
    "Audio",
    "AsyncAudio",
    "AudioWithRawResponse",
    "AsyncAudioWithRawResponse",
    "AudioWithStreamingResponse",
    "AsyncAudioWithStreamingResponse",
]
