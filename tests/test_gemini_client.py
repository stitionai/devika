"""
Tests for Gemini client implementation.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.llm.gemini_client import Gemini

@pytest.fixture
def mock_config():
    with patch('src.llm.gemini_client.config') as mock:
        mock.get_gemini_api_key.return_value = "test-api-key"
        yield mock

@pytest.fixture
def mock_genai():
    with patch('src.llm.gemini_client.genai') as mock:
        yield mock

@pytest.fixture
def gemini_client(mock_config, mock_genai):
    return Gemini()

def test_init_with_api_key(mock_config, mock_genai):
    """Test client initialization with API key."""
    client = Gemini()
    mock_genai.configure.assert_called_once_with(api_key="test-api-key")

def test_init_without_api_key(mock_config, mock_genai):
    """Test client initialization without API key."""
    mock_config.get_gemini_api_key.return_value = None
    with pytest.raises(ValueError, match="Gemini API key not found in configuration"):
        Gemini()

def test_init_config_failure(mock_config, mock_genai):
    """Test handling of configuration failure."""
    mock_genai.configure.side_effect = Exception("Test error")
    with pytest.raises(ValueError, match="Failed to configure Gemini client: Test error"):
        Gemini()

def test_inference_success(mock_genai, gemini_client):
    """Test successful text generation."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Generated response"
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    response = gemini_client.inference("gemini-pro", "Test prompt")
    assert response == "Generated response"
    mock_model.generate_content.assert_called_once_with("Test prompt", safety_settings={
        mock_genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: mock_genai.types.HarmBlockThreshold.BLOCK_NONE,
        mock_genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: mock_genai.types.HarmBlockThreshold.BLOCK_NONE,
    })

def test_inference_empty_response(mock_genai, gemini_client):
    """Test handling of empty response."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = None
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    with pytest.raises(ValueError, match="Error: Unable to generate content Gemini API"):
        gemini_client.inference("gemini-pro", "Test prompt")

def test_inference_error(mock_genai, gemini_client):
    """Test handling of inference error."""
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("Test error")
    mock_genai.GenerativeModel.return_value = mock_model

    with pytest.raises(ValueError, match="Error: Unable to generate content Gemini API"):
        gemini_client.inference("gemini-pro", "Test prompt")

def test_str_representation(gemini_client):
    """Test string representation."""
    assert str(gemini_client) == "Gemini"
