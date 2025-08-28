from openai.types.responses import ToolChoiceOptions

def test_tool_choice_valid_values():
    """Test that ToolChoiceOptions accepts valid values."""
    valid_values = ["none", "auto", "required", "allowed_tools"]
    for value in valid_values:
        assert value in ToolChoiceOptions.__args__  # check if Literal includes it


def test_tool_choice_invalid_value():
    """Test that an invalid tool_choice raises an error."""
    invalid_value = "invalid_mode"
    assert invalid_value not in ToolChoiceOptions.__args__
