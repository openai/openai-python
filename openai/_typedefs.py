import sys
from abc import abstractmethod
from asyncio import StreamReader
from typing import Union, Iterator, Dict, Tuple, TypedDict, List, Optional, AnyStr

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

RawResponseBody: TypeAlias = Union[Iterator[bytes], StreamReader]
HeadersType: TypeAlias = Dict[str, str]
ParamsType: TypeAlias = HeadersType
ProxyType: TypeAlias = Union[str, Dict[str, str]]
RequestTimeoutType: TypeAlias = Union[float, Tuple[float, float]]

_ContentType: TypeAlias = str


class _SupportsRead(Protocol):
    @abstractmethod
    def read(self, n: int = -1) -> AnyStr:
        pass


FileType: TypeAlias = Union[_SupportsRead, str, bytes, bytearray]
FilesType: TypeAlias = List[
    Union[Tuple[str, Tuple[None, str]], Tuple[str, Tuple[str, FileType, _ContentType]]]
]


class AppInfo(TypedDict):
    name: str
    version: Optional[str]
    url: Optional[str]
