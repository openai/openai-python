from __future__ import annotations

import pytest

from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_poll_method_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.vector_stores.files.create,
        checking_client.vector_stores.files.create_and_poll,
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_upload_and_poll_method_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.vector_stores.files.create,
        checking_client.vector_stores.files.upload_and_poll,
        exclude_params={"file_id", "extra_headers", "extra_query", "extra_body", "timeout"},
    )
