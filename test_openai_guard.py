import pytest

from openai import OpenAI

from src.openai.patch_openai import patch_openai_client # Importe ton patch

# Applique le patch une seule fois pour toute la session de test
@pytest.fixture(autouse=True)
def setup_patch():
    patch_openai_client()

def test_heuristic_block_incoherent_prompt():
    # Ici, le patch est déjà actif grâce à la fixture autouse
    client = OpenAI(api_key="sk-fake")
    
    # Ton test attend une ValueError, pas une AuthenticationError
    with pytest.raises(ValueError, match="BLOCKED"):
        client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "fais truc"}]
        )