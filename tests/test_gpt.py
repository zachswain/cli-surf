"""
QA tests for gpt.py
Make sure pytest is installed: pip install pytest
Run pytest: pytest
"""

from unittest.mock import Mock, patch

from src.gpt import openai_gpt, simple_gpt


def test_simple_gpt():
    """Mock g4f Client and verify response returned."""
    mock_message = Mock()
    mock_message.content = "Looks like great surf today!"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("src.gpt.Client", return_value=mock_client):
        result = simple_gpt("surf is 4ft", "give me a report")

    assert result == "Looks like great surf today!"
    mock_client.chat.completions.create.assert_called_once()


def test_openai_gpt():
    """Mock OpenAI client and verify api_key and model passed."""
    mock_message = Mock()
    mock_message.content = "OpenAI surf report"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("src.gpt.OpenAI", return_value=mock_client) as mock_cls:
        result = openai_gpt(
            "surf is 4ft", "give me a report", "sk-test-key", "gpt-4"
        )

    assert result == "OpenAI surf report"
    mock_cls.assert_called_once_with(api_key="sk-test-key")
    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args
    assert call_kwargs.kwargs["model"] == "gpt-4"


def test_simple_gpt_message_content():
    """Verify the prompt concatenation passed to the model."""
    mock_message = Mock()
    mock_message.content = "ok"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("src.gpt.Client", return_value=mock_client):
        simple_gpt("SUMMARY", "PROMPT")

    call_kwargs = mock_client.chat.completions.create.call_args
    messages = call_kwargs.kwargs["messages"]
    assert messages[0]["content"] == "SUMMARYPROMPT"
