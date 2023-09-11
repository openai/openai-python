import openai
import pytest


API_BASE = ""
AZURE_API_KEY = ""
OPENAI_API_KEY = ""
API_VERSION  = ""
AUDIO_FILE_PATH = ""
AUDIO_FILE_NAME = ""


# TRANSCRIBE -----------------------------------------------------------------------------------
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
    openai.api_base = "https://api.openai.com/v1"
    openai.api_type = "openai"
    openai.api_key = OPENAI_API_KEY
    openai.api_version = None
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
        file=open(AUDIO_FILE_PATH, "rb"),
        response_format="verbose_json"
    )
    assert audio


@pytest.mark.asyncio
async def test_atranscribe():

    # Invalid
    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe(
            "whisper-1",
            open(AUDIO_FILE_PATH, "rb"),
            "api_key",
            "api_base",
            "api_type",
            "api_version",
            "organization",
            "extra",
        )
    assert str(e.value) == "atranscribe() takes from 3 to 8 positional arguments but 9 were given"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe()
    assert str(e.value) == "atranscribe() missing 2 required positional argument(s): model, file"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe(
            "whisper-1"
        )
    assert str(e.value) == "atranscribe() missing 1 required positional argument(s): file"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe(
            model="whisper-1"
        )
    assert str(e.value) == "atranscribe() missing 1 required positional argument(s): file"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe(
            file=open(AUDIO_FILE_PATH, "rb")
        )
    assert str(e.value) == "atranscribe() missing 1 required positional argument(s): model"

    # # Valid
    openai.api_base = "https://api.openai.com/v1"
    openai.api_type = "openai"
    openai.api_key = OPENAI_API_KEY
    openai.api_version = None
    audio = await openai.Audio.atranscribe(
        "whisper-1",
        open(AUDIO_FILE_PATH, "rb")
    )
    assert audio

    audio1 = await openai.Audio.atranscribe(
        model="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb")
    )
    assert audio1

    openai.api_base = API_BASE
    openai.api_key = AZURE_API_KEY
    openai.api_type = "azure"
    openai.api_version = API_VERSION
    audio = await openai.Audio.atranscribe(
        deployment_id="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb"),
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
            filename=AUDIO_FILE_NAME
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
            filename=AUDIO_FILE_NAME
        )
    assert str(e.value) == "transcribe_raw() missing 1 required positional argument(s): file"


    with pytest.raises(TypeError) as e:
        openai.Audio.transcribe_raw(
            file=open(AUDIO_FILE_PATH, "rb").read(),
            filename=AUDIO_FILE_NAME
        )
    assert str(e.value) == "transcribe_raw() missing 1 required positional argument(s): model"


    # Valid
    openai.api_base = "https://api.openai.com/v1"
    openai.api_type = "openai"
    openai.api_key = OPENAI_API_KEY
    openai.api_version = None
    audio = openai.Audio.transcribe_raw(
        "whisper-1",
        open(AUDIO_FILE_PATH, "rb").read(),
        AUDIO_FILE_NAME
    )
    assert audio

    audio = openai.Audio.transcribe_raw(
        model="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb").read(),
        filename=AUDIO_FILE_NAME
    )
    assert audio

    openai.api_base = API_BASE
    openai.api_key = AZURE_API_KEY
    openai.api_type = "azure"
    openai.api_version = API_VERSION
    audio = openai.Audio.transcribe_raw(
        deployment_id="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb").read(),
        filename=AUDIO_FILE_NAME
    )
    assert audio


@pytest.mark.asyncio
async def test_atranscribe_raw():

    # Invalid
    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe_raw(
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
    assert str(e.value) == "atranscribe_raw() takes from 4 to 9 positional arguments but 10 were given"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe_raw()
    assert str(e.value) == "atranscribe_raw() missing 3 required positional argument(s): model, file, filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe_raw(
            "whisper-1"
        )
    assert str(e.value) == "atranscribe_raw() missing 2 required positional argument(s): file, filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe_raw(
            "whisper-1",
            open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "atranscribe_raw() missing 1 required positional argument(s): filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe_raw(
            model="whisper-1"
        )
    assert str(e.value) == "atranscribe_raw() missing 2 required positional argument(s): file, filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe_raw(
            file=open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "atranscribe_raw() missing 2 required positional argument(s): model, filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe_raw(
            filename=AUDIO_FILE_NAME
        )
    assert str(e.value) == "atranscribe_raw() missing 2 required positional argument(s): model, file"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe_raw(
            model="whisper-1",
            file=open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "atranscribe_raw() missing 1 required positional argument(s): filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe_raw(
            model="whisper-1",
            filename=AUDIO_FILE_NAME
        )
    assert str(e.value) == "atranscribe_raw() missing 1 required positional argument(s): file"


    with pytest.raises(TypeError) as e:
        await openai.Audio.atranscribe_raw(
            file=open(AUDIO_FILE_PATH, "rb").read(),
            filename=AUDIO_FILE_NAME
        )
    assert str(e.value) == "atranscribe_raw() missing 1 required positional argument(s): model"


    # Valid
    openai.api_base = "https://api.openai.com/v1"
    openai.api_type = "openai"
    openai.api_key = OPENAI_API_KEY
    openai.api_version = None
    audio = await openai.Audio.atranscribe_raw(
        "whisper-1",
        open(AUDIO_FILE_PATH, "rb").read(),
        AUDIO_FILE_NAME
    )
    assert audio

    audio = await openai.Audio.atranscribe_raw(
        model="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb").read(),
        filename=AUDIO_FILE_NAME
    )
    assert audio

    openai.api_base = API_BASE
    openai.api_key = AZURE_API_KEY
    openai.api_type = "azure"
    openai.api_version = API_VERSION
    audio = await openai.Audio.atranscribe_raw(
        deployment_id="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb").read(),
        filename=AUDIO_FILE_NAME
    )
    assert audio


# TRANSLATE -----------------------------------------------------------------------------------

def test_translate():

    # Invalid
    with pytest.raises(TypeError) as e:
        openai.Audio.translate(
            "whisper-1",
            open(AUDIO_FILE_PATH, "rb"),
            "api_key",
            "api_base",
            "api_type",
            "api_version",
            "organization",
            "extra",
        )
    assert str(e.value) == "translate() takes from 3 to 8 positional arguments but 9 were given"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate()
    assert str(e.value) == "translate() missing 2 required positional argument(s): model, file"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate(
            "whisper-1"
        )
    assert str(e.value) == "translate() missing 1 required positional argument(s): file"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate(
            model="whisper-1"
        )
    assert str(e.value) == "translate() missing 1 required positional argument(s): file"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate(
            file=open(AUDIO_FILE_PATH, "rb")
        )
    assert str(e.value) == "translate() missing 1 required positional argument(s): model"

    # # Valid
    openai.api_base = "https://api.openai.com/v1"
    openai.api_type = "openai"
    openai.api_key = OPENAI_API_KEY
    openai.api_version = None
    audio = openai.Audio.translate(
        "whisper-1",
        open(AUDIO_FILE_PATH, "rb")
    )
    assert audio

    audio1 = openai.Audio.translate(
        model="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb")
    )
    assert audio1

    openai.api_base = API_BASE
    openai.api_key = AZURE_API_KEY
    openai.api_type = "azure"
    openai.api_version = API_VERSION
    audio = openai.Audio.translate(
        deployment_id="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb"),
    )
    assert audio


@pytest.mark.asyncio
async def test_atranslate():

    # Invalid
    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate(
            "whisper-1",
            open(AUDIO_FILE_PATH, "rb"),
            "api_key",
            "api_base",
            "api_type",
            "api_version",
            "organization",
            "extra",
        )
    assert str(e.value) == "atranslate() takes from 3 to 8 positional arguments but 9 were given"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate()
    assert str(e.value) == "atranslate() missing 2 required positional argument(s): model, file"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate(
            "whisper-1"
        )
    assert str(e.value) == "atranslate() missing 1 required positional argument(s): file"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate(
            model="whisper-1"
        )
    assert str(e.value) == "atranslate() missing 1 required positional argument(s): file"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate(
            file=open(AUDIO_FILE_PATH, "rb")
        )
    assert str(e.value) == "atranslate() missing 1 required positional argument(s): model"

    # # Valid
    openai.api_base = "https://api.openai.com/v1"
    openai.api_type = "openai"
    openai.api_key = OPENAI_API_KEY
    openai.api_version = None
    audio = await openai.Audio.atranslate(
        "whisper-1",
        open(AUDIO_FILE_PATH, "rb")
    )
    assert audio

    audio1 = await openai.Audio.atranslate(
        model="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb")
    )
    assert audio1

    openai.api_base = API_BASE
    openai.api_key = AZURE_API_KEY
    openai.api_type = "azure"
    openai.api_version = API_VERSION
    audio = await openai.Audio.atranslate(
        deployment_id="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb"),
    )
    assert audio


def test_translate_raw():

    # Invalid
    with pytest.raises(TypeError) as e:
        openai.Audio.translate_raw(
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
    assert str(e.value) == "translate_raw() takes from 4 to 9 positional arguments but 10 were given"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate_raw()
    assert str(e.value) == "translate_raw() missing 3 required positional argument(s): model, file, filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate_raw(
            "whisper-1"
        )
    assert str(e.value) == "translate_raw() missing 2 required positional argument(s): file, filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate_raw(
            "whisper-1",
            open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "translate_raw() missing 1 required positional argument(s): filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate_raw(
            model="whisper-1"
        )
    assert str(e.value) == "translate_raw() missing 2 required positional argument(s): file, filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate_raw(
            file=open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "translate_raw() missing 2 required positional argument(s): model, filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate_raw(
            filename=AUDIO_FILE_NAME
        )
    assert str(e.value) == "translate_raw() missing 2 required positional argument(s): model, file"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate_raw(
            model="whisper-1",
            file=open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "translate_raw() missing 1 required positional argument(s): filename"

    with pytest.raises(TypeError) as e:
        openai.Audio.translate_raw(
            model="whisper-1",
            filename=AUDIO_FILE_NAME
        )
    assert str(e.value) == "translate_raw() missing 1 required positional argument(s): file"


    with pytest.raises(TypeError) as e:
        openai.Audio.translate_raw(
            file=open(AUDIO_FILE_PATH, "rb").read(),
            filename=AUDIO_FILE_NAME
        )
    assert str(e.value) == "translate_raw() missing 1 required positional argument(s): model"


    # Valid
    openai.api_base = "https://api.openai.com/v1"
    openai.api_type = "openai"
    openai.api_key = OPENAI_API_KEY
    openai.api_version = None
    audio = openai.Audio.translate_raw(
        "whisper-1",
        open(AUDIO_FILE_PATH, "rb").read(),
        AUDIO_FILE_NAME
    )
    assert audio

    audio = openai.Audio.translate_raw(
        model="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb").read(),
        filename=AUDIO_FILE_NAME
    )
    assert audio

    openai.api_base = API_BASE
    openai.api_key = AZURE_API_KEY
    openai.api_type = "azure"
    openai.api_version = API_VERSION
    audio = openai.Audio.translate_raw(
        deployment_id="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb").read(),
        filename=AUDIO_FILE_NAME
    )
    assert audio


@pytest.mark.asyncio
async def test_atranslate_raw():

    # Invalid
    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate_raw(
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
    assert str(e.value) == "atranslate_raw() takes from 4 to 9 positional arguments but 10 were given"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate_raw()
    assert str(e.value) == "atranslate_raw() missing 3 required positional argument(s): model, file, filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate_raw(
            "whisper-1"
        )
    assert str(e.value) == "atranslate_raw() missing 2 required positional argument(s): file, filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate_raw(
            "whisper-1",
            open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "atranslate_raw() missing 1 required positional argument(s): filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate_raw(
            model="whisper-1"
        )
    assert str(e.value) == "atranslate_raw() missing 2 required positional argument(s): file, filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate_raw(
            file=open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "atranslate_raw() missing 2 required positional argument(s): model, filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate_raw(
            filename=AUDIO_FILE_NAME
        )
    assert str(e.value) == "atranslate_raw() missing 2 required positional argument(s): model, file"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate_raw(
            model="whisper-1",
            file=open(AUDIO_FILE_PATH, "rb").read()
        )
    assert str(e.value) == "atranslate_raw() missing 1 required positional argument(s): filename"

    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate_raw(
            model="whisper-1",
            filename=AUDIO_FILE_NAME
        )
    assert str(e.value) == "atranslate_raw() missing 1 required positional argument(s): file"


    with pytest.raises(TypeError) as e:
        await openai.Audio.atranslate_raw(
            file=open(AUDIO_FILE_PATH, "rb").read(),
            filename=AUDIO_FILE_NAME
        )
    assert str(e.value) == "atranslate_raw() missing 1 required positional argument(s): model"


    # Valid
    openai.api_base = "https://api.openai.com/v1"
    openai.api_type = "openai"
    openai.api_key = OPENAI_API_KEY
    openai.api_version = None
    audio = await openai.Audio.atranslate_raw(
        "whisper-1",
        open(AUDIO_FILE_PATH, "rb").read(),
        AUDIO_FILE_NAME
    )
    assert audio

    audio = await openai.Audio.atranslate_raw(
        model="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb").read(),
        filename=AUDIO_FILE_NAME
    )
    assert audio

    openai.api_base = API_BASE
    openai.api_key = AZURE_API_KEY
    openai.api_type = "azure"
    openai.api_version = API_VERSION
    audio = await openai.Audio.atranslate_raw(
        deployment_id="whisper-1",
        file=open(AUDIO_FILE_PATH, "rb").read(),
        filename=AUDIO_FILE_NAME
    )
    assert audio
