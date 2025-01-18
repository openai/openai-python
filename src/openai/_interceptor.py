from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, TypeVar, Generic, Any, Union

import httpx

from ._types import Body

T = TypeVar("T")

@dataclass
class InterceptorRequest:
    """Request data container for interceptor processing"""
    method: str
    url: str
    headers: Dict[str, str]
    params: Optional[Dict[str, Any]] = None
    body: Optional[Union[Body, bytes]] = None

@dataclass
class InterceptorResponse(Generic[T]):
    """Response data container for interceptor processing"""
    status_code: int
    headers: Dict[str, str]
    body: T
    request: InterceptorRequest
    raw_response: httpx.Response

class Interceptor(ABC):
    """Base class for request/response interceptors"""

    @abstractmethod
    def before_request(self, request: InterceptorRequest) -> InterceptorRequest:
        """Process request before sending"""
        pass

    @abstractmethod
    def after_response(self, response: InterceptorResponse[T]) -> InterceptorResponse[T]:
        """Process response after receiving"""
        pass

class InterceptorChain:
    """Chain of interceptors for sequential request/response processing"""

    def __init__(self, interceptors: Optional[list[Interceptor]] = None):
        self._interceptors = interceptors or []

    def add_interceptor(self, interceptor: Interceptor) -> None:
        self._interceptors.append(interceptor)

    def execute_before_request(self, request: InterceptorRequest) -> InterceptorRequest:
        current_request = request
        for interceptor in self._interceptors:
            try:
                current_request = interceptor.before_request(current_request)
            except Exception as e:
                continue
        return current_request

    def execute_after_response(self, response: InterceptorResponse[T]) -> InterceptorResponse[T]:
        current_response = response
        for interceptor in self._interceptors:
            try:
                current_response = interceptor.after_response(current_response)
            except Exception as e:
                continue
        return current_response 