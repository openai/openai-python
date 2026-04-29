from openai._compat import parse_obj
from openai.types.moderation import CategoryScores


def test_moderation_category_scores_allows_nullable_illicit_fields() -> None:
    scores = parse_obj(
        CategoryScores,
        {
            "harassment": 0.0,
            "harassment/threatening": 0.0,
            "hate": 0.0,
            "hate/threatening": 0.0,
            "illicit": None,
            "illicit/violent": None,
            "self-harm": 0.0,
            "self-harm/instructions": 0.0,
            "self-harm/intent": 0.0,
            "sexual": 0.0,
            "sexual/minors": 0.0,
            "violence": 0.0,
            "violence/graphic": 0.0,
        },
    )

    assert scores.illicit is None
    assert scores.illicit_violent is None
    assert scores.to_dict() == {
        "harassment": 0.0,
        "harassment/threatening": 0.0,
        "hate": 0.0,
        "hate/threatening": 0.0,
        "illicit": None,
        "illicit/violent": None,
        "self-harm": 0.0,
        "self-harm/instructions": 0.0,
        "self-harm/intent": 0.0,
        "sexual": 0.0,
        "sexual/minors": 0.0,
        "violence": 0.0,
        "violence/graphic": 0.0,
    }
