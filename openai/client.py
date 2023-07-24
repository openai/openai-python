import sys
import time

from typing import (
    Union,
    Any,
    Dict,
    cast,
    Iterable,
    BinaryIO,
    Optional,
    Mapping,
    TYPE_CHECKING
)
if sys.version_info >= (3, 8):
    from typing import Literal, AsyncIterable
else:
    from typing_extensions import Literal, AsyncIterable

import openai

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


LATEST_AZURE_API_VERSION = "2023-05-15"


class AzureTokenAuth:
    """Authentication using an Azure Active Directory token.
    """

    def __repr__(self) -> str:
        return f"AzureTokenAuth({type(self._credential)})"

    def __init__(self, *, credential: Optional["TokenCredential"] = None) -> None:
        """Create a new AzureTokenAuth instance. Requires the
        azure-identity package.

        :keyword credential: A credential type from the azure.identity library.
         If no credential is passed, it will use ~azure.identity.DefaultAzureCredential. 
        :paramtype credential: ~azure.core.credentials.TokenCredential or 
         ~azure.identity.DefaultAzureCredential 
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
        """Gets a valid AAD token to authenticate the request.
        
        .. note:: 

            Do not directly interact with this API, it will be called
            automatically when a token is needed for the request.
        """
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

    def __repr__(self) -> str:
        return "ApiKeyAuth(api_key=<redacted>)"

    def __init__(self, key: str = "") -> None:
        """Create a new ApiKeyAuth instance.

        :param str key: The API key associated with your account.
         If no key is passed, it will use ~openai.api_key
        """
        self.key = key or openai.api_key

    def get_token(self) -> str:
        """Get the API key
        
        .. note:: 

            Do not directly interact with this API, it will be called
            automatically when a token is needed for the request.
        """
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
       :keyword auth: The authentication method or key to use. If the string value "azuredefault" is passed,
        it will use ~azure.identity.DefaultAzureCredential
       :paramtype auth: str or ~openai.client.ApiKeyAuth or ~openai.client.AzureTokenAuth
       :keyword str api_version: The API version to use. If not specified, based on ~openai.api_version
        or ~openai.client.LATEST_AZURE_API_VERSION.
       :keyword str backend: One of 'azure' or 'openai'. If not specified, inferred from the auth method or ~openai.api_type
       :keyword str organization: The identifier of the organization to use for API requests.
        If not specified, based on ~openai.organization.
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

    def __repr__(self) -> str:
        constructor_args = [
            f"{name}={repr(value)}"
            for name, value in self.__dict__.items()
            if value is not None
        ]
        return f"OpenAIClient({','.join(constructor_args)})"
    
    def _populate_args(self, kwargs: Dict[str, Any], **overrides) -> None:
        """Populate default arguments based on the current client configuration/defaults

        :param kwargs: The keyword arguments to send in the API request.
        :param overrides: The user arguments provided to the client method.
        """
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

        :param kwargs: The keyword arguments to send in the API request.
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

    def completion(
        self,
        prompt: Union[str, Iterable[str], Iterable[int], Iterable[Iterable[int]]],
        *,
        model: str = ...,
        deployment_id: str = ...,
        suffix: str = ...,
        max_tokens: int = ...,
        temperature: float = ...,
        top_p: float = ...,
        n: int = ...,
        logprobs: int = ...,
        echo: bool = ...,
        stop: Union[str, Iterable[str]] = ...,
        presence_penalty: float = ...,
        frequency_penalty: float = ...,
        best_of: int = ...,
        logit_bias: Mapping[int, int] = ...,
        user: str = ...,
        **kwargs: Any
    ) -> openai.Completion:
        """Creates a completion for the provided prompt and parameters.

        :param prompt: The prompt(s) to generate completions for,
         encoded as a string, array of strings, array of tokens, 
         or array of token arrays.
        :keyword model: ID of the model or deployment to use.
        :keyword deployment_id: ID of the deployment to use.
        :keyword suffix: The suffix that comes after a completion of inserted text.
        :keyword max_tokens: The maximum number of tokens to generate in the completion.
        :keyword temperature: What sampling temperature to use, between 0 and 2.
         Higher values like 0.8 will make the output more random, while lower values
         like 0.2 will make it more focused and deterministic.
        :keyword top_p: An alternative to sampling with temperature, called
         nucleus sampling, where the model considers the results of the tokens with
         top_p probability mass. So 0.1 means only the tokens comprising the top 10%
         probability mass are considered.
        :keyword n: How many completions to generate for each prompt.
        :keyword logprobs: Include the log probabilities on the logprobs most
         likely tokens, as well the chosen tokens. For example, if logprobs is 5,
         the API will return a list of the 5 most likely tokens. The API will always
         return the logprob of the sampled token, so there may be up to logprobs+1
         elements in the response. The maximum value for logprobs is 5.
        :keyword echo: Echo back the prompt in addition to the completion.
        :keyword stop: Up to 4 sequences where the API will stop generating further tokens.
         The returned text will not contain the stop sequence.
        :keyword presence_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on whether they appear in the text so far, increasing
         the model's likelihood to talk about new topics.
        :keyword frequency_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on their existing frequency in the text so far,
         decreasing the model's likelihood to repeat the same line verbatim.
        :keyword best_of: Generates best_of completions server-side and returns
         the "best" (the one with the highest log probability per token).
         When used with n, best_of controls the number of candidate completions and
         n specifies how many to return - best_of must be greater than n.
        :keyword logit_bias: Modify the likelihood of specified tokens appearing
         in the completion.
        :keyword user: A unique identifier representing your end-user, which can 
         help OpenAI to monitor and detect abuse.
        """
        self._populate_args(
            kwargs,
            model=model,
            deployment_id=deployment_id,
            suffix=suffix,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            logprobs=logprobs,
            echo=echo,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            best_of=best_of,
            logit_bias=logit_bias,
            user=user,
            prompt=prompt,
            stream=False
        )
        self._normalize_model(kwargs)
        return cast(openai.Completion, openai.Completion.create(**kwargs))

    async def acompletion(
        self,
        prompt: Union[str, Iterable[str], Iterable[int], Iterable[Iterable[int]]],
        *,
        model: str = ...,
        deployment_id: str = ...,
        suffix: str = ...,
        max_tokens: int = ...,
        temperature: float = ...,
        top_p: float = ...,
        n: int = ...,
        logprobs: int = ...,
        echo: bool = ...,
        stop: Union[str, Iterable[str]] = ...,
        presence_penalty: float = ...,
        frequency_penalty: float = ...,
        best_of: int = ...,
        logit_bias: Mapping[int, int] = ...,
        user: str = ...,
        **kwargs: Any
    ) -> openai.Completion:
        """Creates a completion for the provided prompt and parameters.

        :param prompt: The prompt(s) to generate completions for,
         encoded as a string, array of strings, array of tokens, 
         or array of token arrays.
        :keyword model: ID of the model or deployment to use.
        :keyword deployment_id: ID of the deployment to use.
        :keyword suffix: The suffix that comes after a completion of inserted text.
        :keyword max_tokens: The maximum number of tokens to generate in the completion.
        :keyword temperature: What sampling temperature to use, between 0 and 2.
         Higher values like 0.8 will make the output more random, while lower values
         like 0.2 will make it more focused and deterministic.
        :keyword top_p: An alternative to sampling with temperature, called
         nucleus sampling, where the model considers the results of the tokens with
         top_p probability mass. So 0.1 means only the tokens comprising the top 10%
         probability mass are considered.
        :keyword n: How many completions to generate for each prompt.
        :keyword logprobs: Include the log probabilities on the logprobs most
         likely tokens, as well the chosen tokens. For example, if logprobs is 5,
         the API will return a list of the 5 most likely tokens. The API will always
         return the logprob of the sampled token, so there may be up to logprobs+1
         elements in the response. The maximum value for logprobs is 5.
        :keyword echo: Echo back the prompt in addition to the completion.
        :keyword stop: Up to 4 sequences where the API will stop generating further tokens.
         The returned text will not contain the stop sequence.
        :keyword presence_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on whether they appear in the text so far, increasing
         the model's likelihood to talk about new topics.
        :keyword frequency_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on their existing frequency in the text so far,
         decreasing the model's likelihood to repeat the same line verbatim.
        :keyword best_of: Generates best_of completions server-side and returns
         the "best" (the one with the highest log probability per token).
         When used with n, best_of controls the number of candidate completions and
         n specifies how many to return - best_of must be greater than n.
        :keyword logit_bias: Modify the likelihood of specified tokens appearing
         in the completion.
        :keyword user: A unique identifier representing your end-user, which can 
         help OpenAI to monitor and detect abuse.
        """
        self._populate_args(
            kwargs,
            model=model,
            deployment_id=deployment_id,
            suffix=suffix,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            logprobs=logprobs,
            echo=echo,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            best_of=best_of,
            logit_bias=logit_bias,
            user=user,
            prompt=prompt,
            stream=False
        )
        self._normalize_model(kwargs)
        return cast(openai.Completion, await openai.Completion.acreate(**kwargs))

    def iter_completion(
        self,
        prompt: Union[str, Iterable[str], Iterable[int], Iterable[Iterable[int]]],
        *,
        model: str = ...,
        deployment_id: str = ...,
        suffix: str = ...,
        max_tokens: int = ...,
        temperature: float = ...,
        top_p: float = ...,
        n: int = ...,
        logprobs: int = ...,
        echo: bool = ...,
        stop: Union[str, Iterable[str]] = ...,
        presence_penalty: float = ...,
        frequency_penalty: float = ...,
        best_of: int = ...,
        logit_bias: Mapping[int, int] = ...,
        user: str = ...,
        **kwargs: Any
    ) -> Iterable[openai.Completion]:
        """Creates a streaming completion for the provided prompt and parameters.

        :param prompt: The prompt(s) to generate completions for,
         encoded as a string, array of strings, array of tokens, 
         or array of token arrays.
        :keyword model: ID of the model or deployment to use.
        :keyword deployment_id: ID of the deployment to use.
        :keyword suffix: The suffix that comes after a completion of inserted text.
        :keyword max_tokens: The maximum number of tokens to generate in the completion.
        :keyword temperature: What sampling temperature to use, between 0 and 2.
         Higher values like 0.8 will make the output more random, while lower values
         like 0.2 will make it more focused and deterministic.
        :keyword top_p: An alternative to sampling with temperature, called
         nucleus sampling, where the model considers the results of the tokens with
         top_p probability mass. So 0.1 means only the tokens comprising the top 10%
         probability mass are considered.
        :keyword n: How many completions to generate for each prompt.
        :keyword logprobs: Include the log probabilities on the logprobs most
         likely tokens, as well the chosen tokens. For example, if logprobs is 5,
         the API will return a list of the 5 most likely tokens. The API will always
         return the logprob of the sampled token, so there may be up to logprobs+1
         elements in the response. The maximum value for logprobs is 5.
        :keyword echo: Echo back the prompt in addition to the completion.
        :keyword stop: Up to 4 sequences where the API will stop generating further tokens.
         The returned text will not contain the stop sequence.
        :keyword presence_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on whether they appear in the text so far, increasing
         the model's likelihood to talk about new topics.
        :keyword frequency_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on their existing frequency in the text so far,
         decreasing the model's likelihood to repeat the same line verbatim.
        :keyword best_of: Generates best_of completions server-side and returns
         the "best" (the one with the highest log probability per token).
         When used with n, best_of controls the number of candidate completions and
         n specifies how many to return - best_of must be greater than n.
        :keyword logit_bias: Modify the likelihood of specified tokens appearing
         in the completion.
        :keyword user: A unique identifier representing your end-user, which can 
         help OpenAI to monitor and detect abuse.
        """
        self._populate_args(
            kwargs,
            model=model,
            deployment_id=deployment_id,
            suffix=suffix,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            logprobs=logprobs,
            echo=echo,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            best_of=best_of,
            logit_bias=logit_bias,
            user=user,
            prompt=prompt,
            stream=True
        )
        self._normalize_model(kwargs)
        return cast(
            Iterable[openai.Completion], openai.Completion.create(**kwargs)
        )

    async def aiter_completion(
        self,
        prompt: Union[str, Iterable[str], Iterable[int], Iterable[Iterable[int]]],
        *,
        model: str = ...,
        deployment_id: str = ...,
        suffix: str = ...,
        max_tokens: int = ...,
        temperature: float = ...,
        top_p: float = ...,
        n: int = ...,
        logprobs: int = ...,
        echo: bool = ...,
        stop: Union[str, Iterable[str]] = ...,
        presence_penalty: float = ...,
        frequency_penalty: float = ...,
        best_of: int = ...,
        logit_bias: Mapping[int, int] = ...,
        user: str = ...,
        **kwargs: Any
    ) -> AsyncIterable[openai.Completion]:
        """Creates a streaming completion for the provided prompt and parameters.

        :param prompt: The prompt(s) to generate completions for,
         encoded as a string, array of strings, array of tokens, 
         or array of token arrays.
        :keyword model: ID of the model or deployment to use.
        :keyword deployment_id: ID of the deployment to use.
        :keyword suffix: The suffix that comes after a completion of inserted text.
        :keyword max_tokens: The maximum number of tokens to generate in the completion.
        :keyword temperature: What sampling temperature to use, between 0 and 2.
         Higher values like 0.8 will make the output more random, while lower values
         like 0.2 will make it more focused and deterministic.
        :keyword top_p: An alternative to sampling with temperature, called
         nucleus sampling, where the model considers the results of the tokens with
         top_p probability mass. So 0.1 means only the tokens comprising the top 10%
         probability mass are considered.
        :keyword n: How many completions to generate for each prompt.
        :keyword logprobs: Include the log probabilities on the logprobs most
         likely tokens, as well the chosen tokens. For example, if logprobs is 5,
         the API will return a list of the 5 most likely tokens. The API will always
         return the logprob of the sampled token, so there may be up to logprobs+1
         elements in the response. The maximum value for logprobs is 5.
        :keyword echo: Echo back the prompt in addition to the completion.
        :keyword stop: Up to 4 sequences where the API will stop generating further tokens.
         The returned text will not contain the stop sequence.
        :keyword presence_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on whether they appear in the text so far, increasing
         the model's likelihood to talk about new topics.
        :keyword frequency_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on their existing frequency in the text so far,
         decreasing the model's likelihood to repeat the same line verbatim.
        :keyword best_of: Generates best_of completions server-side and returns
         the "best" (the one with the highest log probability per token).
         When used with n, best_of controls the number of candidate completions and
         n specifies how many to return - best_of must be greater than n.
        :keyword logit_bias: Modify the likelihood of specified tokens appearing
         in the completion.
        :keyword user: A unique identifier representing your end-user, which can 
         help OpenAI to monitor and detect abuse.
        """
        self._populate_args(
            kwargs,
            model=model,
            deployment_id=deployment_id,
            suffix=suffix,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            logprobs=logprobs,
            echo=echo,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            best_of=best_of,
            logit_bias=logit_bias,
            user=user,
            prompt=prompt,
            stream=True
        )
        self._normalize_model(kwargs)
        return cast(
            AsyncIterable[openai.Completion],
            await openai.Completion.acreate(**kwargs),
        )

    def chatcompletion(
        self,
        messages: Iterable[Mapping[str, Any]],
        *,
        model: str = ...,
        deployment_id: str = ...,
        functions: Iterable[Mapping[str, Any]] = ...,
        function_call: Union[str, Mapping[str, Any]] = ...,
        temperature: float = ...,
        top_p: float = ...,
        n: int = ...,
        stop: Union[str, Iterable[str]] = ...,
        max_tokens: int = ...,
        presence_penalty: float = ...,
        frequency_penalty: float = ...,
        logit_bias: Mapping[int, int] = ...,
        user: str = ...,
        **kwargs: Any
    ) -> openai.ChatCompletion:
        """Creates a model response for the given chat conversation.

        :param messages: A list of messages comprising the conversation so far.
        :keyword model: ID of the model or deployment to use.
        :keyword deployment_id: ID of the deployment to use.
        :keyword functions: A list of functions the model may generate JSON inputs for.
        :keyword function_call: Controls how the model responds to function calls.
         "none" means the model does not call a function, and responds to the
         end-user. "auto" means the model can pick between an end-user or calling
         a function. Specifying a particular function via {"name": "my_function"}
         forces the model to call that function. "none" is the default when no
         functions are present. "auto" is the default if functions are present.
        :keyword temperature: What sampling temperature to use, between 0 and 2.
         Higher values like 0.8 will make the output more random, while lower values
         like 0.2 will make it more focused and deterministic.
        :keyword top_p: An alternative to sampling with temperature, called
         nucleus sampling, where the model considers the results of the tokens with
         top_p probability mass. So 0.1 means only the tokens comprising the top 10%
         probability mass are considered.
        :keyword n: How many completions to generate for each prompt.
        :keyword stop: Up to 4 sequences where the API will stop generating further tokens.
         The returned text will not contain the stop sequence.
        :keyword max_tokens: The maximum number of tokens to generate in the completion.
        :keyword presence_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on whether they appear in the text so far, increasing
         the model's likelihood to talk about new topics.
        :keyword frequency_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on their existing frequency in the text so far,
         decreasing the model's likelihood to repeat the same line verbatim.
        :keyword logit_bias: Modify the likelihood of specified tokens appearing
         in the completion.
        :keyword user: A unique identifier representing your end-user, which can 
         help OpenAI to monitor and detect abuse.
        """
        self._populate_args(
            kwargs,
            messages=messages,
            model=model,
            deployment_id=deployment_id,
            functions=functions,
            function_call=function_call,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            user=user,
            stream=False
        )
        self._normalize_model(kwargs)
        return cast(
            openai.ChatCompletion, openai.ChatCompletion.create(**kwargs)
        )

    async def achatcompletion(
        self,
        messages: Iterable[Mapping[str, Any]],
        *,
        model: str = ...,
        deployment_id: str = ...,
        functions: Iterable[Mapping[str, Any]] = ...,
        function_call: Union[str, Mapping[str, Any]] = ...,
        temperature: float = ...,
        top_p: float = ...,
        n: int = ...,
        stop: Union[str, Iterable[str]] = ...,
        max_tokens: int = ...,
        presence_penalty: float = ...,
        frequency_penalty: float = ...,
        logit_bias: Mapping[int, int] = ...,
        user: str = ...,
        **kwargs: Any
    ) -> openai.ChatCompletion:
        """Creates a model response for the given chat conversation.

        :param messages: A list of messages comprising the conversation so far.
        :keyword model: ID of the model or deployment to use.
        :keyword deployment_id: ID of the deployment to use.
        :keyword functions: A list of functions the model may generate JSON inputs for.
        :keyword function_call: Controls how the model responds to function calls.
         "none" means the model does not call a function, and responds to the
         end-user. "auto" means the model can pick between an end-user or calling
         a function. Specifying a particular function via {"name": "my_function"}
         forces the model to call that function. "none" is the default when no
         functions are present. "auto" is the default if functions are present.
        :keyword temperature: What sampling temperature to use, between 0 and 2.
         Higher values like 0.8 will make the output more random, while lower values
         like 0.2 will make it more focused and deterministic.
        :keyword top_p: An alternative to sampling with temperature, called
         nucleus sampling, where the model considers the results of the tokens with
         top_p probability mass. So 0.1 means only the tokens comprising the top 10%
         probability mass are considered.
        :keyword n: How many completions to generate for each prompt.
        :keyword stop: Up to 4 sequences where the API will stop generating further tokens.
         The returned text will not contain the stop sequence.
        :keyword max_tokens: The maximum number of tokens to generate in the completion.
        :keyword presence_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on whether they appear in the text so far, increasing
         the model's likelihood to talk about new topics.
        :keyword frequency_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on their existing frequency in the text so far,
         decreasing the model's likelihood to repeat the same line verbatim.
        :keyword logit_bias: Modify the likelihood of specified tokens appearing
         in the completion.
        :keyword user: A unique identifier representing your end-user, which can 
         help OpenAI to monitor and detect abuse.
        """
        self._populate_args(
            kwargs,
            messages=messages,
            model=model,
            deployment_id=deployment_id,
            functions=functions,
            function_call=function_call,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            user=user,
            stream=False
        )
        self._populate_args(kwargs, messages=messages, stream=False)
        self._normalize_model(kwargs)
        return cast(
            openai.ChatCompletion, await openai.ChatCompletion.acreate(**kwargs)
        )

    def iter_chatcompletion(
        self,
        messages: Iterable[Mapping[str, Any]],
        *,
        model: str = ...,
        deployment_id: str = ...,
        functions: Iterable[Mapping[str, Any]] = ...,
        function_call: Union[str, Mapping[str, Any]] = ...,
        temperature: float = ...,
        top_p: float = ...,
        n: int = ...,
        stop: Union[str, Iterable[str]] = ...,
        max_tokens: int = ...,
        presence_penalty: float = ...,
        frequency_penalty: float = ...,
        logit_bias: Mapping[int, int] = ...,
        user: str = ...,
        **kwargs: Any
    ) -> Iterable[openai.ChatCompletion]:
        """Creates a streaming model response for the given chat conversation.

        :param messages: A list of messages comprising the conversation so far.
        :keyword model: ID of the model or deployment to use.
        :keyword deployment_id: ID of the deployment to use.
        :keyword functions: A list of functions the model may generate JSON inputs for.
        :keyword function_call: Controls how the model responds to function calls.
         "none" means the model does not call a function, and responds to the
         end-user. "auto" means the model can pick between an end-user or calling
         a function. Specifying a particular function via {"name": "my_function"}
         forces the model to call that function. "none" is the default when no
         functions are present. "auto" is the default if functions are present.
        :keyword temperature: What sampling temperature to use, between 0 and 2.
         Higher values like 0.8 will make the output more random, while lower values
         like 0.2 will make it more focused and deterministic.
        :keyword top_p: An alternative to sampling with temperature, called
         nucleus sampling, where the model considers the results of the tokens with
         top_p probability mass. So 0.1 means only the tokens comprising the top 10%
         probability mass are considered.
        :keyword n: How many completions to generate for each prompt.
        :keyword stop: Up to 4 sequences where the API will stop generating further tokens.
         The returned text will not contain the stop sequence.
        :keyword max_tokens: The maximum number of tokens to generate in the completion.
        :keyword presence_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on whether they appear in the text so far, increasing
         the model's likelihood to talk about new topics.
        :keyword frequency_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on their existing frequency in the text so far,
         decreasing the model's likelihood to repeat the same line verbatim.
        :keyword logit_bias: Modify the likelihood of specified tokens appearing
         in the completion.
        :keyword user: A unique identifier representing your end-user, which can 
         help OpenAI to monitor and detect abuse.
        """
        self._populate_args(
            kwargs,
            messages=messages,
            model=model,
            deployment_id=deployment_id,
            functions=functions,
            function_call=function_call,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            user=user,
            stream=True
        )
        self._normalize_model(kwargs)
        return cast(
            Iterable[openai.ChatCompletion],
            openai.ChatCompletion.create(**kwargs),
        )

    async def aiter_chatcompletion(
        self,
        messages: Iterable[Mapping[str, Any]],
        *,
        model: str = ...,
        deployment_id: str = ...,
        functions: Iterable[Mapping[str, Any]] = ...,
        function_call: Union[str, Mapping[str, Any]] = ...,
        temperature: float = ...,
        top_p: float = ...,
        n: int = ...,
        stop: Union[str, Iterable[str]] = ...,
        max_tokens: int = ...,
        presence_penalty: float = ...,
        frequency_penalty: float = ...,
        logit_bias: Mapping[int, int] = ...,
        user: str = ...,
        **kwargs: Any
    ) -> AsyncIterable[openai.ChatCompletion]:
        """Creates a streaming model response for the given chat conversation.

        :param messages: A list of messages comprising the conversation so far.
        :keyword model: ID of the model or deployment to use.
        :keyword deployment_id: ID of the deployment to use.
        :keyword functions: A list of functions the model may generate JSON inputs for.
        :keyword function_call: Controls how the model responds to function calls.
         "none" means the model does not call a function, and responds to the
         end-user. "auto" means the model can pick between an end-user or calling
         a function. Specifying a particular function via {"name": "my_function"}
         forces the model to call that function. "none" is the default when no
         functions are present. "auto" is the default if functions are present.
        :keyword temperature: What sampling temperature to use, between 0 and 2.
         Higher values like 0.8 will make the output more random, while lower values
         like 0.2 will make it more focused and deterministic.
        :keyword top_p: An alternative to sampling with temperature, called
         nucleus sampling, where the model considers the results of the tokens with
         top_p probability mass. So 0.1 means only the tokens comprising the top 10%
         probability mass are considered.
        :keyword n: How many completions to generate for each prompt.
        :keyword stop: Up to 4 sequences where the API will stop generating further tokens.
         The returned text will not contain the stop sequence.
        :keyword max_tokens: The maximum number of tokens to generate in the completion.
        :keyword presence_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on whether they appear in the text so far, increasing
         the model's likelihood to talk about new topics.
        :keyword frequency_penalty: Number between -2.0 and 2.0. Positive values
         penalize new tokens based on their existing frequency in the text so far,
         decreasing the model's likelihood to repeat the same line verbatim.
        :keyword logit_bias: Modify the likelihood of specified tokens appearing
         in the completion.
        :keyword user: A unique identifier representing your end-user, which can 
         help OpenAI to monitor and detect abuse.
        """
        self._populate_args(
            kwargs,
            messages=messages,
            model=model,
            deployment_id=deployment_id,
            functions=functions,
            function_call=function_call,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            user=user,
            stream=True
        )
        self._normalize_model(kwargs)
        return cast(
            AsyncIterable[openai.ChatCompletion],
            await openai.ChatCompletion.acreate(**kwargs),
        )

    def embeddings(
        self,
        input: Union[str, Iterable[str], Iterable[int], Iterable[Iterable[int]]],
        *,
        model: str = ...,
        deployment_id: str = ...,
        user: str = ...,
        **kwargs: Any
    ) -> openai.Embedding:
        """Creates an embedding vector representing the input text.

        :param input: Input text to embed, encoded as a string or array
         of tokens. To embed multiple inputs in a single request, pass
         an array of strings or array of token arrays. Each input must
         not exceed the max input tokens for the model (8191 tokens for 
         text-embedding-ada-002)
        :keyword model: ID of the model or deployment to use.
        :keyword deployment_id: ID of the deployment to use.
        :keyword user: A unique identifier representing your end-user, which can 
         help OpenAI to monitor and detect abuse.
        """
        self._populate_args(
            kwargs,
            input=input,
            model=model,
            deployment_id=deployment_id,
            user=user,
        )
        self._normalize_model(kwargs)
        return cast(openai.Embedding, openai.Embedding.create(**kwargs))

    async def aembeddings(
        self,
        input: Union[str, Iterable[str], Iterable[int], Iterable[Iterable[int]]],
        *,
        model: str = ...,
        deployment_id: str = ...,
        user: str = ...,
        **kwargs: Any
    ) -> openai.Embedding:
        """Creates an embedding vector representing the input text.

        :param input: Input text to embed, encoded as a string or array
         of tokens. To embed multiple inputs in a single request, pass
         an array of strings or array of token arrays. Each input must
         not exceed the max input tokens for the model (8191 tokens for 
         text-embedding-ada-002)
        :keyword model: ID of the model or deployment to use.
        :keyword deployment_id: ID of the deployment to use.
        :keyword user: A unique identifier representing your end-user, which can 
         help OpenAI to monitor and detect abuse.
        """
        self._populate_args(
            kwargs,
            input=input,
            model=model,
            deployment_id=deployment_id,
            user=user,
        )
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
        **kwargs: Any,
    ) -> openai.Image:
        """Creates an image given a prompt.

        :param prompt: A text description of the desired image(s). The maximum length is 1000 characters.
        :keyword n: The number of images to generate. Must be between 1 and 10.
        :keyword size: The size of the generated images. Must be one of 256x256, 512x512, or 1024x1024.
        :keyword response_format: The format in which the generated images are returned.
         Must be one of url or b64_json.
        :keyword user: A unique identifier representing your end-user, which can help OpenAI to
         monitor and detect abuse.
        """
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
        **kwargs: Any,
    ) -> openai.Image:
        """Creates an image given a prompt.

        :param prompt: A text description of the desired image(s). The maximum length is 1000 characters.
        :keyword n: The number of images to generate. Must be between 1 and 10.
        :keyword size: The size of the generated images. Must be one of 256x256, 512x512, or 1024x1024.
        :keyword response_format: The format in which the generated images are returned.
         Must be one of url or b64_json.
        :keyword user: A unique identifier representing your end-user, which can help OpenAI to
         monitor and detect abuse.
        """
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
        **kwargs: Any,
    ) -> openai.Image:
        """Creates a variation of a given image.

        :param image: The image to use as the basis for the variation(s).
         Must be a valid PNG file, less than 4MB, and square.
        :keyword n: The number of images to generate. Must be between 1 and 10.
        :keyword size: The size of the generated images. Must be one of 256x256, 512x512, or 1024x1024.
        :keyword response_format: The format in which the generated images are returned.
         Must be one of url or b64_json.
        :keyword user: A unique identifier representing your end-user, which can help OpenAI to
         monitor and detect abuse.
        """
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
        **kwargs: Any,
    ) -> openai.Image:
        """Creates a variation of a given image.

        :param image: The image to use as the basis for the variation(s).
         Must be a valid PNG file, less than 4MB, and square.
        :keyword n: The number of images to generate. Must be between 1 and 10.
        :keyword size: The size of the generated images. Must be one of 256x256, 512x512, or 1024x1024.
        :keyword response_format: The format in which the generated images are returned.
         Must be one of url or b64_json.
        :keyword user: A unique identifier representing your end-user, which can help OpenAI to
         monitor and detect abuse.
        """
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
        **kwargs: Any,
    ) -> openai.Image:
        """Creates an edited or extended image given an original image and a prompt.

        :param image: The image to edit. Must be a valid PNG file, less than 4MB, and square.
         If mask is not provided, image must have transparency, which will be used as the mask.
        :param prompt: A text description of the desired image(s). The maximum length is 1000 characters.
        :keyword mask: An additional image whose fully transparent areas (e.g. where alpha is zero)
         indicate where image should be edited. Must be a valid PNG file, less than 4MB, and have the
         same dimensions as image.
        :keyword n: The number of images to generate. Must be between 1 and 10.
        :keyword size: The size of the generated images. Must be one of 256x256, 512x512, or 1024x1024.
        :keyword response_format: The format in which the generated images are returned.
         Must be one of url or b64_json.
        :keyword user: A unique identifier representing your end-user, which can help OpenAI to
         monitor and detect abuse.
        """
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
        **kwargs: Any,
    ) -> openai.Image:
        """Creates an edited or extended image given an original image and a prompt.

        :param image: The image to edit. Must be a valid PNG file, less than 4MB, and square.
         If mask is not provided, image must have transparency, which will be used as the mask.
        :param prompt: A text description of the desired image(s). The maximum length is 1000 characters.
        :keyword mask: An additional image whose fully transparent areas (e.g. where alpha is zero)
         indicate where image should be edited. Must be a valid PNG file, less than 4MB, and have the
         same dimensions as image.
        :keyword n: The number of images to generate. Must be between 1 and 10.
        :keyword size: The size of the generated images. Must be one of 256x256, 512x512, or 1024x1024.
        :keyword response_format: The format in which the generated images are returned.
         Must be one of url or b64_json.
        :keyword user: A unique identifier representing your end-user, which can help OpenAI to
         monitor and detect abuse.
        """
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

    def moderation(
        self,
        input: Union[str, Iterable[str]],
        *,
        model: str = ...,
        **kwargs: Any,
    ) -> openai.Moderation:
        """Classifies if text violates OpenAI's Content Policy.

        :param input: The input text to classify.
        :keyword model: ID of the model to use.
        """
        self._populate_args(
            kwargs,
            input=input,
            model=model,
        )
        self._normalize_model(kwargs)
        kwargs.pop("api_base")
        kwargs.pop("api_type")
        kwargs.pop("organization")
        return cast(openai.Moderation, openai.Moderation.create(**kwargs))

    async def amoderation(
        self,
        input: Union[str, Iterable[str]],
        *,
        model: str = ...,
        **kwargs: Any,
    ) -> openai.Moderation:
        """Classifies if text violates OpenAI's Content Policy.

        :param input: The input text to classify.
        :keyword model: ID of the model to use.
        """
        self._populate_args(
            kwargs,
            input=input,
            model=model,
        )
        self._normalize_model(kwargs)
        kwargs.pop("api_base")
        kwargs.pop("api_type")
        kwargs.pop("organization")
        return cast(openai.Moderation, await openai.Moderation.acreate(**kwargs))

    def transcribe_audio(
        self,
        file: Union[bytes, BinaryIO],
        *,
        model: str = ...,
        prompt: str = ...,
        response_format: str = ...,
        temperature: float = ...,
        language: str = ...,
        **kwargs,
    ) -> openai.Audio:
        """Transcribes audio into the input language.

        :param file: The audio file object (not file name) to transcribe,
         in one of these formats: mp3, mp4, mpeg, mpga, m4a, wav, or webm.
        :keyword model: ID of the model to use.
        :keyword prompt: An optional text to guide the model's style or 
         continue a previous audio segment. The prompt should match the audio language.
        :keyword response_format: The format of the transcript output, in one of 
         these options: json, text, srt, verbose_json, or vtt.
        :keyword temperature: The sampling temperature, between 0 and 1. Higher values 
         like 0.8 will make the output more random, while lower values like 0.2 will 
         make it more focused and deterministic. If set to 0, the model will use log 
         probability to automatically increase the temperature until certain thresholds 
         are hit.
        :keyword language: The language of the input audio. Supplying the input 
         language in ISO-639-1 format will improve accuracy and latency.
        """
        self._populate_args(
            kwargs,
            file=file,
            model=model,
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
        model: str = ...,
        prompt: str = ...,
        response_format: str = ...,
        temperature: float = ...,
        language: str = ...,
        **kwargs,
    ) -> openai.Audio:
        """Transcribes audio into the input language.

        :param file: The audio file object (not file name) to transcribe,
         in one of these formats: mp3, mp4, mpeg, mpga, m4a, wav, or webm.
        :keyword model: ID of the model to use. Only whisper-1 is currently available.
        :keyword prompt: An optional text to guide the model's style or 
         continue a previous audio segment. The prompt should match the audio language.
        :keyword response_format: The format of the transcript output, in one of 
         these options: json, text, srt, verbose_json, or vtt.
        :keyword temperature: The sampling temperature, between 0 and 1. Higher values 
         like 0.8 will make the output more random, while lower values like 0.2 will 
         make it more focused and deterministic. If set to 0, the model will use log 
         probability to automatically increase the temperature until certain thresholds 
         are hit.
        :keyword language: The language of the input audio. Supplying the input 
         language in ISO-639-1 format will improve accuracy and latency.
        """
        self._populate_args(
            kwargs,
            file=file,
            model=model,
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
        model: str = ...,
        prompt: str = ...,
        response_format: str = ...,
        temperature: float = ...,
        **kwargs,
    ) -> openai.Audio:
        """Translates audio into English.

        :param file: The audio file object (not file name) to transcribe,
         in one of these formats: mp3, mp4, mpeg, mpga, m4a, wav, or webm.
        :keyword model: ID of the model to use. Only whisper-1 is currently available.
        :keyword prompt: An optional text to guide the model's style or 
         continue a previous audio segment. The prompt should be in English.
        :keyword response_format: The format of the transcript output, in one of 
         these options: json, text, srt, verbose_json, or vtt.
        :keyword temperature: The sampling temperature, between 0 and 1. Higher values 
         like 0.8 will make the output more random, while lower values like 0.2 will 
         make it more focused and deterministic. If set to 0, the model will use log 
         probability to automatically increase the temperature until certain thresholds 
         are hit.
        """
        self._populate_args(
            kwargs,
            file=file,
            model=model,
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
        model: str = ...,
        prompt: str = ...,
        response_format: str = ...,
        temperature: float = ...,
        **kwargs,
    ) -> openai.Audio:
        """Translates audio into English.

        :param file: The audio file object (not file name) to transcribe,
         in one of these formats: mp3, mp4, mpeg, mpga, m4a, wav, or webm.
        :keyword model: ID of the model to use. Only whisper-1 is currently available.
        :keyword prompt: An optional text to guide the model's style or 
         continue a previous audio segment. The prompt should be in English.
        :keyword response_format: The format of the transcript output, in one of 
         these options: json, text, srt, verbose_json, or vtt.
        :keyword temperature: The sampling temperature, between 0 and 1. Higher values 
         like 0.8 will make the output more random, while lower values like 0.2 will 
         make it more focused and deterministic. If set to 0, the model will use log 
         probability to automatically increase the temperature until certain thresholds 
         are hit.
        """
        self._populate_args(
            kwargs,
            file=file,
            model=model,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
        )
        self._normalize_model(kwargs)
        return cast(openai.Audio, await openai.Audio.atranslate(**kwargs))
