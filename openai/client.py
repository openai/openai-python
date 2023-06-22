import sys
import time

from typing import Union, Dict, Any, cast, Iterable, BinaryIO
if sys.version_info >= (3, 8):
    from typing import Literal, AsyncIterable
else:
    from typing_extensions import Literal, AsyncIterable

import openai

LATEST_AZURE_API_VERSION = "2023-05-15"


class AzureTokenAuth:
    """Authentication using an Azure AD token.
    """

    def __repr__(self):
        return f"AzureTokenAuth({type(self._credential)})"

    def __init__(self, *, credential=None):
        """Create a new AzureTokenAuth instance. If no credential is passed, 
        it will use ~azure.identity.DefaultAzureCredential
        """
        if not credential:
            try:
                import azure.identity
            except ImportError:
                raise Exception(
                    "You have to install the azure-identity package in order to use AzureTokenAuth"
                )
            credential = azure.identity.DefaultAzureCredential()
        self._credential = credential
        self._cached_token = None

    def get_token(self) -> str:
        if (
            self._cached_token is None
            or (self._cached_token.expires_on - time.time()) < 300
        ):
            self._cached_token = self._credential.get_token(
                "https://cognitiveservices.azure.com/.default"
            )

        return self._cached_token.token


class ApiKeyAuth:
    """Authentication using an API key"""

    def __repr__(self):
        return f"ApiKeyAuth(api_key=<redacted>)"
    
    def __init__(self, key: str = ""):
        """Create a new ApiKeyAuth instance. If no key is passed, it will use ~openai.api_key"""
        self.key = key or openai.api_key

    def get_token(self) -> str:
        """Get the API key"""
        return self.key


Backends = Literal["azure", "openai", ""]


class OpenAIClient:
    def __init__(
        self,
        *,
        api_base: str = "",
        auth: Union[str, ApiKeyAuth, AzureTokenAuth] = "",
        api_version: str = "",
        backend: Backends = "",
        organization: str = "",
    ):
        """Create a new OpenAI client.
           
       :keyword str api_base: The base URL for the API. If not specified, based on ~opeanai.api_base
       :keyword auth: The authentication method or key to use. If the string value "azuredefault" is passed, it will use ~azure.identity.DefaultAzureCredential
       :paramtype auth: str or ~openai.client.ApiKeyAuth or ~openai.client.AzureTokenAuth
       :keyword str api_version: The API version to use. If not specified, based on ~openai.api_version or ~openai.client.LATEST_AZURE_API_VERSION.
       :keyword str backend: One of 'azure' or 'openai'. If not specified, inferred from the auth method or ~openai.api_type
        """

        #
        # This code is a bit messy, but it's because we want to hide the messiness from the caller.
        #
        if auth == "azuredefault":
            self.auth = AzureTokenAuth()
        elif isinstance(auth, str):
            self.auth = ApiKeyAuth(auth or openai.api_key)
        else:
            self.auth = auth

        # Pick up api type from parameter or environment
        self.backend = backend or (
            "azure" if openai.api_type in ("azure", "azure_ad", "azuread") or isinstance(auth, AzureTokenAuth) else "openai"
        )

        if self.backend == "azure":
            self.api_version = (
                api_version or openai.api_version or LATEST_AZURE_API_VERSION
            )
            if isinstance(self.auth, AzureTokenAuth):
                self.api_type = "azure_ad"
            else:
                self.api_type = "azure"
        elif self.backend == "openai":
            self.api_type = "open_ai"
            self.api_version = api_version or openai.api_version
        else:
            raise ValueError(
                f'Unknown `backend` {backend} - expected one of "azure" or "openai"'
            )

        self.api_base = api_base or openai.api_base
        self.organization = organization or openai.organization
        if self.backend == 'azure' and self.api_base == "https://api.openai.com/v1":
            raise ValueError("You are using the 'openai.com' endpoint with an Azure credential or API type. Please provide the endpoint to your Azure resource instead.")

    def __repr__(self): 
        constructor_args = [
            f"{name}={repr(value)}"
            for name, value in self.__dict__.items()
            if value is not None
        ]
        return f"OpenAIClient({','.join(constructor_args)})"
    
    def _populate_args(self, kwargs: Dict[str, Any], **overrides) -> None:
        """Populate default arguments based on the current client configuration/defaults"""
        kwargs.setdefault("api_base", self.api_base or openai.api_base)
        kwargs.setdefault("api_key", self.auth.get_token())
        kwargs.setdefault("api_type", self.api_type)
        kwargs.setdefault("organization", self.organization)
        if self.api_version:
            kwargs.setdefault("api_version", self.api_version)

        for key, val in overrides.items():
            if val == ...:
                continue
            kwargs.setdefault(key, val)
            if kwargs[key] != val:
                raise TypeError(f"No parameter named `{key}`")

    def _normalize_model(self, kwargs: Dict[str, Any]):
        """Normalize model/engine/deployment_id based on which backend the client is
        configured to target.

        Specifically, it will pass the provided `model` parameter as `deployment_id`
        unless `deployment_id` is explicitly passed in.
        """
        if (
            len(
                [
                    param
                    for param in kwargs
                    if param in ("deployment_id", "model", "engine")
                ]
            )
            != 1
        ):
            raise TypeError(
                "You must specify exactly one of `deployment_id`, `model` and `engine`"
            )

        if self.backend == "azure":
            try:
                # We'll try to "rename" the `model` keyword to fit azure's `deployment_id`
                # paradigm
                kwargs["deployment_id"] = kwargs.pop("model")
            except KeyError:
                pass

    def completion(self, prompt: str, **kwargs) -> openai.Completion:
        self._populate_args(kwargs, prompt=prompt, stream=False)
        self._normalize_model(kwargs)
        return cast(openai.Completion, openai.Completion.create(**kwargs))

    async def acompletion(self, prompt: str, **kwargs) -> openai.Completion:
        self._populate_args(kwargs, prompt=prompt, stream=False)
        self._normalize_model(kwargs)
        return cast(openai.Completion, await openai.Completion.acreate(**kwargs))

    def iter_completion(
        self, prompt: str, **kwargs
    ) -> Iterable[openai.Completion]:
        self._populate_args(kwargs, prompt=prompt, stream=True)
        self._normalize_model(kwargs)
        return cast(
            Iterable[openai.Completion], openai.Completion.create(**kwargs)
        )

    async def aiter_completion(
        self, prompt: str, **kwargs
    ) -> AsyncIterable[openai.Completion]:
        self._populate_args(kwargs, prompt=prompt, stream=True)
        self._normalize_model(kwargs)
        return cast(
            AsyncIterable[openai.Completion],
            await openai.Completion.acreate(**kwargs),
        )

    def chatcompletion(self, messages, **kwargs) -> openai.ChatCompletion:
        self._populate_args(kwargs, messages=messages, stream=False)
        self._normalize_model(kwargs)
        return cast(
            openai.ChatCompletion, openai.ChatCompletion.create(**kwargs)
        )

    async def achatcompletion(self, messages, **kwargs) -> openai.ChatCompletion:
        self._populate_args(kwargs, messages=messages, stream=False)
        self._normalize_model(kwargs)
        return cast(
            openai.ChatCompletion, await openai.ChatCompletion.acreate(**kwargs)
        )

    def iter_chatcompletion(
        self, messages, **kwargs
    ) -> Iterable[openai.ChatCompletion]:
        self._populate_args(kwargs, messages=messages, stream=True)
        self._normalize_model(kwargs)
        return cast(
            Iterable[openai.ChatCompletion],
            openai.ChatCompletion.create(**kwargs),
        )

    async def aiter_chatcompletion(
        self, messages, **kwargs
    ) -> AsyncIterable[openai.ChatCompletion]:
        self._populate_args(kwargs, messages=messages, stream=True)
        self._normalize_model(kwargs)
        return cast(
            AsyncIterable[openai.ChatCompletion],
            await openai.ChatCompletion.acreate(**kwargs),
        )

    def embeddings(self, input, **kwargs) -> openai.Embedding:
        self._populate_args(kwargs, input=input)
        self._normalize_model(kwargs)
        return cast(openai.Embedding, openai.Embedding.create(**kwargs))

    async def aembeddings(self, input, **kwargs) -> openai.Embedding:
        self._populate_args(kwargs, input=input)
        self._normalize_model(kwargs)
        return cast(openai.Embedding, await openai.Embedding.acreate(**kwargs))

    def image(
        self,
        prompt: str,
        *,
        n: int = ...,
        size: str = ...,
        response_format: str = ...,
        user: str = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            prompt=prompt,
            n=n,
            size=size,
            response_format=response_format,
            user=user,
        )
        return cast(openai.Image, openai.Image.create(**kwargs))

    async def aimage(
        self,
        prompt: str,
        *,
        n: int = ...,
        size: str = ...,
        response_format: str = ...,
        user: str = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            prompt=prompt,
            n=n,
            size=size,
            response_format=response_format,
            user=user,
        )
        return cast(openai.Image, await openai.Image.acreate(**kwargs))

    def image_variation(
        self,
        image: Union[bytes,  BinaryIO],
        *,
        n: int = ...,
        size: str = ...,
        response_format: str = ...,
        user: str = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            image=image,
            n=n,
            size=size,
            response_format=response_format,
            user=user,
        )
        return cast(openai.Image, openai.Image.create_variation(**kwargs))

    async def aimage_variation(
        self,
        image: Union[bytes, BinaryIO],
        *,
        n: int = ...,
        size: str = ...,
        response_format: str = ...,
        user: str = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            image=image,
            n=n,
            size=size,
            response_format=response_format,
            user=user,
        )
        return cast(openai.Image, await openai.Image.acreate_variation(**kwargs))

    def image_edit(
        self,
        image: Union[bytes, BinaryIO],
        prompt: str,
        *,
        mask: str = ...,
        n: int = ...,
        size: str = ...,
        response_format: str = ...,
        user: str = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            image=image,
            n=n,
            size=size,
            prompt=prompt,
            mask=mask,
            response_format=response_format,
            user=user,
        )
        return cast(openai.Image, openai.Image.create_edit(**kwargs))

    async def aimage_edit(
        self,
        image: Union[bytes, BinaryIO],
        prompt: str,
        *,
        mask: str = ...,
        n: int = ...,
        size: str = ...,
        response_format: str = ...,
        user: str = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            image=image,
            n=n,
            size=size,
            prompt=prompt,
            mask=mask,
            response_format=response_format,
            user=user,
        )
        return cast(openai.Image, await openai.Image.acreate_edit(**kwargs))

    def edit(
        self,
        instruction: str,
        *,
        input: str = ...,
        n: int = ...,
        temperature: float = ...,
        top_p: float = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            instruction=instruction,
            input=input,
            n=n,
            temperature=temperature,
            top_p=top_p,
        )
        self._normalize_model(kwargs)
        return cast(openai.Edit, openai.Edit.create(**kwargs))

    async def aedit(
        self,
        instruction: str,
        *,
        input: str = ...,
        n: int = ...,
        temperature: float = ...,
        top_p: float = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            instruction=instruction,
            input=input,
            n=n,
            temperature=temperature,
            top_p=top_p,
        )
        self._normalize_model(kwargs)
        return cast(openai.Edit, await openai.Edit.acreate(**kwargs))

    def moderation(
        self,
        input: Union[str, Iterable[str]],
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            input=input,
        )
        self._normalize_model(kwargs)
        return cast(openai.Moderation, openai.Moderation.create(**kwargs))

    async def amoderation(
        self,
        input: Union[str, Iterable[str]],
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            input=input,
        )
        self._normalize_model(kwargs)
        return cast(openai.Moderation, await openai.Moderation.acreate(**kwargs))

    def transcribe_audio(
        self,
        file: Union[bytes, BinaryIO],
        *,
        prompt: str = ...,
        response_format: str = ...,
        temperature: float = ...,
        language: str = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            file=file,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
            language=language
        )
        self._normalize_model(kwargs)
        return cast(openai.Audio, openai.Audio.transcribe(**kwargs))

    async def atranscribe_audio(
        self,
        file: Union[bytes, BinaryIO],
        *,
        prompt: str = ...,
        response_format: str = ...,
        temperature: float = ...,
        language: str = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            file=file,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
            language=language
        )
        self._normalize_model(kwargs)
        return cast(openai.Audio, await openai.Audio.atranscribe(**kwargs))

    def translate_audio(
        self,
        file: Union[bytes, BinaryIO],
        *,
        prompt: str = ...,
        response_format: str = ...,
        temperature: float = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            file=file,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
        )
        self._normalize_model(kwargs)
        return cast(openai.Audio, openai.Audio.translate(**kwargs))

    async def atranslate_audio(
        self,
        file: Union[bytes, BinaryIO],
        *,
        prompt: str = ...,
        response_format: str = ...,
        temperature: float = ...,
        **kwargs,
    ):
        self._populate_args(
            kwargs,
            file=file,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
        )
        self._normalize_model(kwargs)
        return cast(openai.Audio, await openai.Audio.atranslate(**kwargs))

if __name__ == "__main__":
    client = OpenAIClient(
        api_base="https://achand-openai-0.openai.azure.com/",
        auth="azuredefault",
        backend="azure",
    )
    print(client.completion("what is up, my friend?", model="chatgpt"))
    # print(client.embeddings("What, or what is this?", model="arch")) # Doesn't work 'cause it is the wrong model...

    import asyncio

    async def stream_chat():
        respco = await client.aiter_completion(
            "what is up, my friend?", model="chatgpt"
        )
        async for rsp in respco:
            print(rsp)

    asyncio.run(stream_chat())

    oaiclient = OpenAIClient()
    print(oaiclient.completion("what is up, my friend?", model="text-davinci-003"))
    print(oaiclient.embeddings("What are embeddings?", model="text-embedding-ada-002"))
    rsp = oaiclient.image("Happy cattle", response_format="b64_json")
    print(rsp)
