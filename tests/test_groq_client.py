import pytest
from unittest.mock import Mock, patch
from requests.exceptions import HTTPError

from src.llm.groq_client import Groq


def test_groq_rate_limit_handling():
    groq = Groq()

    # Mock the Groq client to simulate rate limit error
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception(
        'Rate limit reached for model `mixtral-8x7b-32768`. Please try again in 7.164s.'
    )
    groq.client = mock_client

    # Test that rate limit error is converted to HTTPError
    with pytest.raises(HTTPError) as exc_info:
        groq.inference("mixtral-8x7b-32768", "test prompt")

    assert exc_info.value.response.status_code == 429
    assert "rate limit" in str(exc_info.value.response.content.decode()).lower()


def test_groq_other_error_handling():
    groq = Groq()

    # Mock the Groq client to simulate other error
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("Some other error")
    groq.client = mock_client

    # Test that other errors are re-raised as-is
    with pytest.raises(Exception) as exc_info:
        groq.inference("mixtral-8x7b-32768", "test prompt")

    assert "Some other error" in str(exc_info.value)
    assert not isinstance(exc_info.value, HTTPError)
