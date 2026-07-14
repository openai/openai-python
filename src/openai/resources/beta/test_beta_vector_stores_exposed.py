from openai import OpenAI

def test_beta_vector_stores_exists():
    client = OpenAI(api_key="test")
    assert hasattr(client.beta, "vector_stores")