from typing import TypeVar, Any
import time
from typing_extensions import override
from openai import OpenAI
from openai._interceptor import Interceptor, InterceptorRequest, InterceptorResponse
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T")

# Define a custom logging interceptor
class LoggingInterceptor(Interceptor):
    @override
    def before_request(self, request: InterceptorRequest) -> InterceptorRequest:
        print(f"Request: {request.method} {request.url}")
        print(f"Headers: {request.headers}")
        if request.body:
            print(f"Body: {request.body}")
        return request

    @override
    def after_response(self, response: InterceptorResponse[Any]) -> InterceptorResponse[Any]:
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Body: {response.body}")
        return response

# Define an interceptor that implements retry logic with exponential backoff
class RetryInterceptor(Interceptor):
    def __init__(self, max_retries: int = 3, initial_delay: float = 1.0):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.current_retry = 0

    @override
    def before_request(self, request: InterceptorRequest) -> InterceptorRequest:
        return request

    @override
    def after_response(self, response: InterceptorResponse[Any]) -> InterceptorResponse[Any]:
        # If response is successful or we've exhausted retries, return as is
        if response.status_code < 500 or self.current_retry >= self.max_retries:
            self.current_retry = 0  # Reset for next request
            return response

        # Calculate delay with exponential backoff
        delay = self.initial_delay * (2 ** self.current_retry)
        print(f"Request failed with status {response.status_code}. Retrying in {delay} seconds...")
        time.sleep(delay)
        
        self.current_retry += 1
        # Trigger a retry by raising an exception
        raise Exception(f"Retrying request (attempt {self.current_retry}/{self.max_retries})")

# Initialize the OpenAI client and add interceptors
if __name__ == "__main__":
    # Create the interceptor chain
    logging_interceptor = LoggingInterceptor()
    retry_interceptor = RetryInterceptor(max_retries=3, initial_delay=1.0)

    # Create client with interceptors
    client = OpenAI(
        interceptors=[logging_interceptor, retry_interceptor]
    )

    # Make a request using the client
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Tell me about error handling and retries in software systems."}],
        max_tokens=100,
    )

    # Output the final response
    print("Final Response:", response)
