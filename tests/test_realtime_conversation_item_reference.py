# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from openai.types.realtime import ConversationItem, RealtimeConversationItemReference

from tests.utils import assert_matches_type


def test_conversation_item_reference_matches_type() -> None:
    item = RealtimeConversationItemReference(
        id="item_123",
        type="item_reference",
    )

    assert_matches_type(ConversationItem, item, path=["item"])
