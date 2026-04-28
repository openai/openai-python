from pathlib import Path

import anyio
import pytest
from dirty_equals import IsDict, IsList, IsBytes, IsTuple

from openai._files import to_httpx_files, deepcopy_with_paths, async_to_httpx_files
from openai._utils import extract_files

readme_path = Path(__file__).parent.parent.joinpath("README.md")


def test_pathlib_includes_file_name() -> None:
    result = to_httpx_files({"file": readme_path})
    print(result)
    assert result == IsDict({"file": IsTuple("README.md", IsBytes())})


def test_tuple_input() -> None:
    result = to_httpx_files([("file", readme_path)])
    print(result)
    assert result == IsList(IsTuple("file", IsTuple("README.md", IsBytes())))


@pytest.mark.asyncio
async def test_async_pathlib_includes_file_name() -> None:
    result = await async_to_httpx_files({"file": readme_path})
    print(result)
    assert result == IsDict({"file": IsTuple("README.md", IsBytes())})


@pytest.mark.asyncio
async def test_async_supports_anyio_path() -> None:
    result = await async_to_httpx_files({"file": anyio.Path(readme_path)})
    print(result)
    assert result == IsDict({"file": IsTuple("README.md", IsBytes())})


@pytest.mark.asyncio
async def test_async_tuple_input() -> None:
    result = await async_to_httpx_files([("file", readme_path)])
    print(result)
    assert result == IsList(IsTuple("file", IsTuple("README.md", IsBytes())))


def test_string_not_allowed() -> None:
    with pytest.raises(TypeError, match="Expected file types input to be a FileContent type or to be a tuple"):
        to_httpx_files(
            {
                "file": "foo",  # type: ignore
            }
        )


def assert_different_identities(obj1: object, obj2: object) -> None:
    assert obj1 == obj2
    assert obj1 is not obj2


class TestDeepcopyWithPaths:
    def test_copies_top_level_dict(self) -> None:
        original = {"file": b"data", "other": "value"}
        result = deepcopy_with_paths(original, [["file"]])
        assert_different_identities(result, original)

    def test_file_value_is_same_reference(self) -> None:
        file_bytes = b"contents"
        original = {"file": file_bytes}
        result = deepcopy_with_paths(original, [["file"]])
        assert_different_identities(result, original)
        assert result["file"] is file_bytes

    def test_list_popped_wholesale(self) -> None:
        files = [b"f1", b"f2"]
        original = {"files": files, "title": "t"}
        result = deepcopy_with_paths(original, [["files", "<array>"]])
        assert_different_identities(result, original)
        result_files = result["files"]
        assert isinstance(result_files, list)
        assert_different_identities(result_files, files)

    def test_nested_array_path_copies_list_and_elements(self) -> None:
        elem1 = {"file": b"f1", "extra": 1}
        elem2 = {"file": b"f2", "extra": 2}
        original = {"items": [elem1, elem2]}
        result = deepcopy_with_paths(original, [["items", "<array>", "file"]])
        assert_different_identities(result, original)
        result_items = result["items"]
        assert isinstance(result_items, list)
        assert_different_identities(result_items, original["items"])
        assert_different_identities(result_items[0], elem1)
        assert_different_identities(result_items[1], elem2)

    def test_empty_paths_returns_same_object(self) -> None:
        original = {"foo": "bar"}
        result = deepcopy_with_paths(original, [])
        assert result is original

    def test_multiple_paths(self) -> None:
        f1 = b"file1"
        f2 = b"file2"
        original = {"a": f1, "b": f2, "c": "unchanged"}
        result = deepcopy_with_paths(original, [["a"], ["b"]])
        assert_different_identities(result, original)
        assert result["a"] is f1
        assert result["b"] is f2
        assert result["c"] is original["c"]

    def test_extract_files_does_not_mutate_original_top_level(self) -> None:
        file_bytes = b"contents"
        original = {"file": file_bytes, "other": "value"}

        copied = deepcopy_with_paths(original, [["file"]])
        extracted = extract_files(copied, paths=[["file"]])

        assert extracted == [("file", file_bytes)]
        assert original == {"file": file_bytes, "other": "value"}
        assert copied == {"other": "value"}

    def test_extract_files_does_not_mutate_original_nested_array_path(self) -> None:
        file1 = b"f1"
        file2 = b"f2"
        original = {
            "items": [
                {"file": file1, "extra": 1},
                {"file": file2, "extra": 2},
            ],
            "title": "example",
        }

        copied = deepcopy_with_paths(original, [["items", "<array>", "file"]])
        extracted = extract_files(copied, paths=[["items", "<array>", "file"]])

        assert extracted == [("items[][file]", file1), ("items[][file]", file2)]
        assert original == {
            "items": [
                {"file": file1, "extra": 1},
                {"file": file2, "extra": 2},
            ],
            "title": "example",
        }
        assert copied == {
            "items": [
                {"extra": 1},
                {"extra": 2},
            ],
            "title": "example",
        }
