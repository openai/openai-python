import time
import typing

import openai

LATEST_AZURE_API_VERSION = "2023-05-15"


class AzureTokenAuth:
    def __init__(self, credential=None):
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
        if self._cached_token is None or (self._cached_token.expires_on - time.time()) < 300:
            self._cached_token = self._credential.get_token(
                "https://cognitiveservices.azure.com/.default"
            )

        return self._cached_token.token


class ApiKeyAuth:
    def __init__(self, key: str = ""):
        self.key = key or openai.api_key

    def get_token(self) -> str:
        return self.key


Backends = typing.Literal["azure", "openai", ""]


class OpenAIClient:

    def __init__(
        self,
        *,
        api_base: str = "",
        auth: typing.Union[str, ApiKeyAuth, AzureTokenAuth] = "",
        api_version: str = "",
        backend: Backends = "",
    ):
        self.api_base = api_base or openai.api_base
        if auth == "azuredefault":
            self.auth = AzureTokenAuth()
        elif isinstance(auth, str):
            self.auth = ApiKeyAuth(auth or openai.api_key)
        else:
            self.auth = auth

        # Pick up api type from parameter or environment
        backend = backend or (
            "azure" if openai.api_type in ("azure", "azure_ad") else "openai"
        )

        self.backend = backend

        if backend == "azure":
            self.api_version = (
                api_version or openai.api_version or LATEST_AZURE_API_VERSION
            )
            if isinstance(self.auth, AzureTokenAuth):
                self.api_type = "azure_ad"
            else:
                self.api_type = "azure"
        elif backend in ("openai", ""):
            self.api_type = "open_ai"
            self.api_version = api_version or openai.api_version
        else:
            raise ValueError(
                f'Unknown `backend` {backend} - expected one of "azure" or "openai"'
            )

    def _populate_args(self, kwargs: typing.Dict[str, typing.Any], **overrides) -> None:
        """Populate default arguments based on the current client configuration/defaults
        """
        kwargs.setdefault("api_base", self.api_base or openai.api_base)
        kwargs.setdefault("api_key", self.auth.get_token())
        kwargs.setdefault("api_type", self.api_type)
        if self.api_version:
            kwargs.setdefault("api_version", self.api_version)

        for key, val in overrides.items():
            if val == ...:
                continue
            kwargs.setdefault(key, val)
            if kwargs[key] != val:
                raise TypeError(f"No parameter named `{key}`")

    def _normalize_model(self, kwargs: typing.Dict[str, typing.Any]):
        """Normalize model/engine/deployment_id based on which backend the client is
           configured to target.

           Specifically, it will pass the provided `model` parameter as `deployment_id`
           unless `deployment_id` is explicitly passed in.
        """
        if len([param for param in kwargs if param in ('deployment_id', 'model', 'engine')]) != 1:
            raise TypeError('You can only specify one of `deployment_id`, `model` and `engine`')
        
        if self.backend == 'azure':
            try:
                # We'll try to "rename" the `model` keyword to fit azure's `deployment_id`
                # paradigm
                kwargs['deployment_id'] = kwargs.pop('model')
            except KeyError:
                pass

    def completion(self, prompt: str, **kwargs) -> openai.Completion:
        self._populate_args(kwargs, prompt=prompt, stream=False)
        self._normalize_model(kwargs)
        return typing.cast(openai.Completion, openai.Completion.create(**kwargs))

    async def acompletion(self, prompt: str, **kwargs) -> openai.Completion:
        self._populate_args(kwargs, prompt=prompt, stream=False)
        self._normalize_model(kwargs)
        return typing.cast(openai.Completion, await openai.Completion.acreate(**kwargs))

    def iter_completion(
        self, prompt: str, **kwargs
    ) -> typing.Iterable[openai.Completion]:
        self._populate_args(kwargs, prompt=prompt, stream=True)
        self._normalize_model(kwargs)
        return typing.cast(
            typing.Iterable[openai.Completion], openai.Completion.create(**kwargs)
        )

    async def aiter_completion(
        self, prompt: str, **kwargs
    ) -> typing.AsyncIterable[openai.Completion]:
        self._populate_args(kwargs, prompt=prompt, stream=True)
        self._normalize_model(kwargs)
        return typing.cast(
            typing.AsyncIterable[openai.Completion], await openai.Completion.acreate(**kwargs)
        )

    def chatcompletion(self, messages, **kwargs) -> openai.ChatCompletion:
        self._populate_args(kwargs, messages=messages, stream=False)
        self._normalize_model(kwargs)
        return typing.cast(
            openai.ChatCompletion, openai.ChatCompletion.create(**kwargs)
        )

    async def achatcompletion(self, messages, **kwargs) -> openai.ChatCompletion:
        self._populate_args(kwargs, messages=messages, stream=False)
        self._normalize_model(kwargs)
        return typing.cast(
            openai.ChatCompletion, await openai.ChatCompletion.acreate(**kwargs)
        )

    def iter_chatcompletion(
        self, messages, **kwargs
    ) -> typing.Iterable[openai.ChatCompletion]:
        self._populate_args(kwargs, messages=messages, stream=True)
        self._normalize_model(kwargs)
        return typing.cast(
            typing.Iterable[openai.ChatCompletion],
            openai.ChatCompletion.create(**kwargs),
        )

    async def aiter_chatcompletion(
        self, messages, **kwargs
    ) -> typing.AsyncIterable[openai.ChatCompletion]:
        self._populate_args(kwargs, messages=messages, stream=True)
        self._normalize_model(kwargs)
        return typing.cast(
            typing.AsyncIterable[openai.ChatCompletion],
            await openai.ChatCompletion.acreate(**kwargs),
        )

    def embeddings(self, input, **kwargs) -> openai.Embedding:
        self._populate_args(kwargs, input=input)
        self._normalize_model(kwargs)
        return typing.cast(openai.Embedding, openai.Embedding.create(**kwargs))

    async def aembeddings(self, input, **kwargs) -> openai.Embedding:
        self._populate_args(kwargs, input=input)
        self._normalize_model(kwargs)
        return typing.cast(openai.Embedding, await openai.Embedding.acreate(**kwargs))

    def image(self, prompt: str, *, n: int = ..., size: str = ...,
              response_format: str = ..., user: str = ...,
              **kwargs):
        self._populate_args(kwargs, prompt = prompt, n  = n, size = size,
                            response_format = response_format, user = user)
        return typing.cast(openai.Image, openai.Image.create(**kwargs))
    
    async def aimage(self, prompt: str, *, n: int = ..., size: str = ...,
              response_format: str = ..., user: str = ...,
              **kwargs):
        self._populate_args(kwargs, prompt = prompt, n  = n, size = size,
                            response_format = response_format, user = user)
        return typing.cast(openai.Image, await openai.Image.acreate(**kwargs))

    def image_variation(self, image: bytes | typing.BinaryIO, *, n: int = ...,
                        size: str = ..., response_format: str = ...,
                        user: str = ..., **kwargs):
        self._populate_args(kwargs, image = image, n  = n, size = size,
                            response_format = response_format, user = user)
        return typing.cast(openai.Image, openai.Image.create_variation(**kwargs))

    async def aimage_variation(self, image: bytes | typing.BinaryIO, *, n: int = ...,
                        size: str = ..., response_format: str = ...,
                        user: str = ..., **kwargs):
        self._populate_args(kwargs, image = image, n = n, size = size,
                            response_format = response_format, user = user)
        return typing.cast(openai.Image, await openai.Image.acreate_variation(**kwargs))

    def image_edit(self, image: bytes | typing.BinaryIO, prompt: str, *, mask: str = ..., n: int = ...,
                        size: str = ..., response_format: str = ...,
                        user: str = ..., **kwargs):
        self._populate_args(kwargs, image = image, n = n, size = size,
                            prompt = prompt, mask = mask,
                            response_format = response_format, user = user)
        return typing.cast(openai.Image, openai.Image.create_edit(**kwargs))
    
    async def aimage_edit(self, image: bytes | typing.BinaryIO, prompt: str, *, mask: str = ..., n: int = ...,
                        size: str = ..., response_format: str = ...,
                        user: str = ..., **kwargs):
        self._populate_args(kwargs, image = image, n = n, size = size,
                            prompt = prompt, mask = mask,
                            response_format = response_format, user = user)
        return typing.cast(openai.Image, await openai.Image.acreate_edit(**kwargs))

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
        respco = await client.aiter_completion("what is up, my friend?", model="chatgpt")
        async for rsp in respco:
            print(rsp)

    asyncio.run(stream_chat())
    

    oaiclient = OpenAIClient()
    print(oaiclient.completion("what is up, my friend?", model="text-davinci-003"))
    print(oaiclient.embeddings("What are embeddings?", model="text-embedding-ada-002"))
    rsp = oaiclient.image("Happy cattle", response_format="b64_json")
    print(rsp)