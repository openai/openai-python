import pytest
import httpx
from typing import Dict, Any, cast, TypeVar
from typing_extensions import override
from openai._interceptor import InterceptorRequest, InterceptorResponse, Interceptor

T = TypeVar("T")

class TestMessageModifierInterceptor:
    def test_before_request_chat_completions(self, caplog: pytest.LogCaptureFixture) -> None:
        class MessageModifierInterceptor(Interceptor):
            @override
            def before_request(self, request: InterceptorRequest) -> InterceptorRequest:
                if isinstance(request.body, dict):
                    body = cast(Dict[str, Any], request.body) # type: ignore
                    if "messages" in body:
                        print("\n=== Message Modification Process ===")
                        for message in body["messages"]:
                            if message["role"] == "user":
                                print(f"Original message: {message['content']}")
                                message["content"] += " [Disclaimer: This is a modified message]"
                                print(f"Modified message: {message['content']}")
                        print("=================================\n")
                return request

            @override
            def after_response(self, response: InterceptorResponse[Any]) -> InterceptorResponse[Any]:
                print("\n=== Response Received ===")
                print(f"Status code: {response.status_code}")
                print(f"Response body: {response.body}")
                print("======================\n")
                return response

        interceptor = MessageModifierInterceptor()
        request = InterceptorRequest(
            method="post",
            url="https://api.openai.com/v1/chat/completions",
            headers={"Authorization": "Bearer test_key"},
            body={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )

        processed_request = interceptor.before_request(request)

        # Verify the message was modified
        assert isinstance(processed_request.body, dict)
        body = cast(Dict[str, Any], processed_request.body) # type: ignore
        assert body["messages"][0]["content"] == "Hello [Disclaimer: This is a modified message]"
        assert body["model"] == "gpt-3.5-turbo"  # Other fields unchanged
        assert processed_request.method == "post"  # Request properties unchanged
        assert processed_request.url == "https://api.openai.com/v1/chat/completions"

    def test_before_request_non_chat_completions(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that the interceptor doesn't modify non-chat-completions requests"""
        class MessageModifierInterceptor(Interceptor):
            @override
            def before_request(self, request: InterceptorRequest) -> InterceptorRequest:
                if isinstance(request.body, dict):
                    body = cast(Dict[str, Any], request.body) # type: ignore
                    if "messages" in body:
                        print("\n=== Message Modification Process ===")
                        for message in body["messages"]:
                            if message["role"] == "user":
                                print(f"Original message: {message['content']}")
                                message["content"] += " [Disclaimer: This is a modified message]"
                                print(f"Modified message: {message['content']}")
                        print("=================================\n")
                return request

            @override
            def after_response(self, response: InterceptorResponse[Any]) -> InterceptorResponse[Any]:
                print("\n=== Response Received ===")
                print(f"Status code: {response.status_code}")
                print(f"Response body: {response.body}")
                print("======================\n")
                return response

        interceptor = MessageModifierInterceptor()
        request = InterceptorRequest(
            method="post",
            url="https://api.openai.com/v1/embeddings",
            headers={"Authorization": "Bearer test_key"},
            body={
                "model": "text-embedding-ada-002",
                "input": "Hello"
            }
        )

        processed_request = interceptor.before_request(request)

        # Verify the request was not modified
        assert isinstance(processed_request.body, dict)
        body = cast(Dict[str, Any], processed_request.body) # type: ignore
        assert body["input"] == "Hello"  # Content unchanged
        assert body["model"] == "text-embedding-ada-002"  # Model unchanged

    def test_after_response(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that after_response doesn't modify the response"""
        class MessageModifierInterceptor(Interceptor):
            @override
            def before_request(self, request: InterceptorRequest) -> InterceptorRequest:
                if isinstance(request.body, dict):
                    body = cast(Dict[str, Any], request.body) # type: ignore
                    if "messages" in body:
                        print("\n=== Message Modification Process ===")
                        for message in body["messages"]:
                            if message["role"] == "user":
                                print(f"Original message: {message['content']}")
                                message["content"] += " [Disclaimer: This is a modified message]"
                                print(f"Modified message: {message['content']}")
                        print("=================================\n")
                return request

            @override
            def after_response(self, response: InterceptorResponse[Any]) -> InterceptorResponse[Any]:
                print("\n=== Response Received ===")
                print(f"Status code: {response.status_code}")
                print(f"Response body: {response.body}")
                print("======================\n")
                return response

        interceptor = MessageModifierInterceptor()
        request = InterceptorRequest(
            method="post",
            url="https://api.openai.com/v1/chat/completions",
            headers={"Authorization": "Bearer test_key"}
        )
        
        mock_raw_response = httpx.Response(
            status_code=200,
            headers={"Content-Type": "application/json"},
            json={"choices": [{"message": {"content": "Hello!"}}]}
        )
        
        response = InterceptorResponse[Dict[str, Any]](
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"choices": [{"message": {"content": "Hello!"}}]},
            request=request,
            raw_response=mock_raw_response
        )

        processed_response = interceptor.after_response(response)
        
        # Verify response is unchanged
        assert processed_response == response
        assert processed_response.status_code == 200
        assert processed_response.body == {"choices": [{"message": {"content": "Hello!"}}]}
