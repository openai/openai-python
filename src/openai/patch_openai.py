"""
PATCH OPENAI CLIENT
-------------------
Ce module effectue un 'Monkey Patch' sur la méthode 'post' du client OpenAI.
Objectif : Intercepter les requêtes sortantes pour vérifier la conformité 
des messages via notre système d'heuristiques (VF - Vérification de Filtre).
Si le score heuristique est invalide, la requête est bloquée avant envoi.
"""


# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownVariableType=false

from typing import Any, Dict, List, cast
from openai._client import SyncAPIClient

def patch_openai_client() -> None:
    from .heuristics import HeuristicGuard

    # On force le type pour calmer l'IDE
    original_post: Any = SyncAPIClient.post

    def patched_post(self: Any, *args: Any, **kwargs: Any) -> Any:
        body: Dict[str, Any] = kwargs.get("body", {})
        messages: List[Dict[str, Any]] = body.get("messages", [])
        
        # On explicite le type pour 'last_msg' pour enlever l'avertissement 'Unknown | str'
        last_msg: str = cast(str, next(
            (m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), 
            ""
        ))
        
        if last_msg:
            analysis: Dict[str, Any] = HeuristicGuard.analyze(last_msg)
            if not analysis.get("valid", True):
                raise ValueError(f"BLOCKED: Score {analysis.get('S', 0)}")
        
        return original_post(self, *args, **kwargs)

    SyncAPIClient.post = patched_post # type: ignore