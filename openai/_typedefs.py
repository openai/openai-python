import io
import sys
from asyncio import StreamReader
from typing import Union, Iterator, Dict, Tuple, TypedDict, List, Optional, IO

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

RawResponseBody: TypeAlias = Union[Iterator[bytes], StreamReader]
HeadersType: TypeAlias = Dict[str, str]
ParamsType: TypeAlias = HeadersType
ProxyType: TypeAlias = Union[str, Dict[str, str]]
RequestTimeoutType: TypeAlias = Union[float, Tuple[float, float]]

_ContentType: TypeAlias = str
FilesType: TypeAlias = List[
    Union[Tuple[str, Tuple[None, str]], Tuple[str, Tuple[str, Union[io.IOBase, IO], _ContentType]]]
]


class AppInfo(TypedDict):
    name: str
    version: Optional[str]
    url: Optional[str]
