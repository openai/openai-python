import json

import pytest

from openai._models import validate_type, construct_type
from openai.types.webhooks import WebhookEndpointWithSecret


@pytest.mark.parametrize("strict", [False, True], ids=["loose", "strict"])
def test_signing_secret_is_hidden_from_representations(strict: bool) -> None:
    secret = "whsec_fake_representation_regression_test"
    payload = {
        "id": "we_test",
        "created_at": 1,
        "event_types": ["response.completed"],
        "name": "Test endpoint",
        "object": "webhook_endpoint",
        "signing_secret": secret,
        "signing_secret_hint": "masked",
        "url": "https://example.com/webhooks",
    }
    factory = validate_type if strict else construct_type
    endpoint = factory(type_=WebhookEndpointWithSecret, value=payload)
    assert isinstance(endpoint, WebhookEndpointWithSecret)

    for rendered in (repr(endpoint), str(endpoint), repr([endpoint])):
        assert secret not in rendered
        assert "we_test" in rendered
        assert "masked" in rendered

    assert endpoint.signing_secret == secret
    assert endpoint.to_dict()["signing_secret"] == secret
    assert json.loads(endpoint.to_json())["signing_secret"] == secret
