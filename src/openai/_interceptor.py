from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, TypeVar, Generic, Any, Union

import httpx

from ._types import Body

T = TypeVar("T")

@dataclass
class InterceptorRequest:
    """Container for request data that can be modified by interceptors"""
    method: str
    url: str
    headers: Dict[str, str]
    params: Optional[Dict[str, Any]] = None
    body: Optional[Union[Body, bytes]] = None

@dataclass
class InterceptorResponse(Generic[T]):
    """Container for response data that can be processed by interceptors"""
    status_code: int
    headers: Dict[str, str]
    body: T
    request: InterceptorRequest
    raw_response: httpx.Response

class Interceptor(ABC):
    """Base class for implementing request/response interceptors"""

    @abstractmethod
    def before_request(self, request: InterceptorRequest) -> InterceptorRequest:
        """Process and optionally modify the request before it is sent.
        
        Args:
            request: The request to process
            
        Returns:
            The processed request
        """
        pass

    @abstractmethod
    def after_response(self, response: InterceptorResponse[T]) -> InterceptorResponse[T]:
        """Process and optionally modify the response after it is received.
        
        Args:
            response: The response to process
            
        Returns:
            The processed response
        """
        pass

class InterceptorChain:
    """Manages a chain of interceptors that process requests/responses in sequence"""

    def __init__(self, interceptors: Optional[list[Interceptor]] = None):
        self._interceptors = interceptors or []

    def add_interceptor(self, interceptor: Interceptor) -> None:
        """Add an interceptor to the chain"""
        self._interceptors.append(interceptor)

    def execute_before_request(self, request: InterceptorRequest) -> InterceptorRequest:
        """Execute all interceptors' before_request methods in sequence"""
        print("\n=== Intercepted Request ===")
        print(f"Method: {request.method}")
        print(f"URL: {request.url}")
        print(f"Headers: {request.headers}")
        if request.params:
            print(f"Query Params: {request.params}")
        if request.body:
            print(f"Request Body: {request.body}")
        print("========================\n")
        
        current_request = request
        for interceptor in self._interceptors:
            try:
                current_request = interceptor.before_request(current_request)
            except Exception as e:
                # Log error but continue processing
                print(f"Error in interceptor {interceptor.__class__.__name__}: {e}")
        return current_request

    def execute_after_response(self, response: InterceptorResponse[T]) -> InterceptorResponse[T]:
        """Execute all interceptors' after_response methods in sequence"""
        print("\n=== Intercepted Response ===")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Response Body: {response.body}")
        print("=========================\n")
        
        current_response = response
        for interceptor in self._interceptors:
            try:
                current_response = interceptor.after_response(current_response)
            except Exception as e:
                # Log error but continue processing
                print(f"Error in interceptor {interceptor.__class__.__name__}: {e}")
        return current_response 