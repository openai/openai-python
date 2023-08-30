import openai
import pytest


API_BASE = ""
AZURE_API_KEY = ""
OPENAI_API_KEY = ""
API_VERSION  = ""
AUDIO_FILE_PATH = ""


def test_transcribe():

    # Invalid
    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe(
            "whisper-1",
            open(AUDIO_FILE_PATH, "rb"),
            "api_key",
            "api_base",
            "api_type",
            "api_version",
            "organization",
            "extra",
        )
    assert str(e.value) == "transcribe() takes from 3 to 8 positional arguments but 9 were given"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe()
    assert str(e.value) == "transcribe() missing 2 required positional argument(s): model, file"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe(
            "whisper-1"
        )
    assert str(e.value) == "transcribe() missing 1 required positional argument(s): file"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe(
            model="whisper-1"
        )
    assert str(e.value) == "transcribe() missing 1 required positional argument(s): file"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe(
            file=open(AUDIO_FILE_PATH, "rb")
        )
    assert str(e.value) == "transcribe() missing 1 required positional argument(s): model"

    # Valid
    openai.api_key = OPENAI_API_KEY
    audio = openai.Audio.transcribe(
        "whisper-1",
        open(AUDIO_FILE_PATH, "rb")
    )
    assert audio

    audio = openai.Audio.transcribe(
        model="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb")
    )
    assert audio

    openai.api_base = API_BASE
    openai.api_key = AZURE_API_KEY
    openai.api_type = "azure"
    openai.api_version = API_VERSION
    audio = openai.Audio.transcribe(
        deployment_id="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb")
    )
    assert audio


def test_transcribe_raw():

    # Invalid
    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe_raw(
            "whisper-1",
            open(AUDIO_FILE_PATH, "rb").read(),
            "filename",
            "api_key",
            "api_base",
            "api_type",
            "api_version",
            "organization",
            "extra",
        )
    assert str(e.value) == "transcribe_raw() takes from 4 to 9 positional arguments but 10 were given"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe_raw()
    assert str(e.value) == "transcribe_raw() missing 3 required positional argument(s): model, file, filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe_raw(
            "whisper-1"
        )
    assert str(e.value) == "transcribe_raw() missing 2 required positional argument(s): file, filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe_raw(
            "whisper-1",
            open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "transcribe_raw() missing 1 required positional argument(s): filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe_raw(
            model="whisper-1"
        )
    assert str(e.value) == "transcribe_raw() missing 2 required positional argument(s): file, filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe_raw(
            file=open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "transcribe_raw() missing 2 required positional argument(s): model, filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe_raw(
            filename="recording.m4a"
        )
    assert str(e.value) == "transcribe_raw() missing 2 required positional argument(s): model, file"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe_raw(
            model="whisper-1",
            file=open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "transcribe_raw() missing 1 required positional argument(s): filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe_raw(
            model="whisper-1",
            filename="recording.m4a"
        )
    assert str(e.value) == "transcribe_raw() missing 1 required positional argument(s): file"


    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe_raw(
            file=open(AUDIO_FILE_PATH, "rb").read(),
            filename="recording.m4a"
        )
    assert str(e.value) == "transcribe_raw() missing 1 required positional argument(s): model"


    # Valid
    openai.api_key = OPENAI_API_KEY
    audio = openai.Audio.transcribe_raw(
        "whisper-1",
        open(AUDIO_FILE_PATH, "rb").read(),
        "recording.m4a"
    )
    assert audio

    audio = openai.Audio.transcribe_raw(
        model="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb").read(),
        filename="recording.m4a"
    )
    assert audio

    openai.api_base = API_BASE
    openai.api_key = AZURE_API_KEY
    openai.api_type = "azure"
    openai.api_version = API_VERSION
    audio = openai.Audio.transcribe_raw(
        deployment_id="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb").read(),
        filename="recording.m4a"
    )
    assert audio
