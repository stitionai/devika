import pytest
import os
import requests
from unittest.mock import patch, MagicMock
from src.llm.ollama_client import Ollama
from src.config import Config

def test_ollama_client_initialization():
    """Test Ollama client initialization with default config"""
    with patch('requests.get') as mock_get, \
         patch('ollama.Client') as mock_client:
        mock_get.return_value = MagicMock(status_code=200)
        mock_client.return_value.list.return_value = {"models": []}

        client = Ollama()
        assert client.host == Config().get_ollama_api_endpoint()
        assert client.client is not None
        assert isinstance(client.models, list)

def test_ollama_client_initialization_with_env():
    """Test Ollama client initialization with environment variable"""
    with patch('requests.get') as mock_get, \
         patch('ollama.Client') as mock_client, \
         patch.dict(os.environ, {'OLLAMA_HOST': 'http://ollama-service:11434'}):
        mock_get.return_value = MagicMock(status_code=200)
        mock_client.return_value.list.return_value = {"models": []}

        client = Ollama()
        assert client.host == "http://ollama-service:11434"
        assert client.client is not None

def test_ollama_client_connection_retry():
    """Test Ollama client connection retry logic"""
    with patch('requests.get') as mock_get, \
         patch('ollama.Client') as mock_client, \
         patch('time.sleep') as mock_sleep:
        # Simulate first two failures, then success
        mock_get.side_effect = [
            requests.exceptions.ConnectionError(),
            requests.exceptions.ConnectionError(),
            MagicMock(status_code=200)
        ]
        mock_client.return_value.list.return_value = {"models": []}

        client = Ollama()
        assert client.client is not None
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2

def test_ollama_client_invalid_url():
    """Test Ollama client with invalid URL"""
    with patch.dict(os.environ, {'OLLAMA_HOST': 'invalid-url'}):
        client = Ollama()
        assert client.client is None
        assert len(client.models) == 0

def test_ollama_client_models_list():
    """Test Ollama client models list retrieval"""
    mock_models = {
        "models": [
            {"name": "llama2"},
            {"name": "codellama"}
        ]
    }
    with patch('requests.get') as mock_get, \
         patch('ollama.Client') as mock_client:
        mock_get.return_value = MagicMock(status_code=200)
        mock_client.return_value.list.return_value = mock_models

        client = Ollama()
        assert len(client.models) == 2
        assert client.models[0]["name"] == "llama2"
        assert client.models[1]["name"] == "codellama"

def test_ollama_client_inference():
    """Test Ollama client inference"""
    mock_models = {
        "models": [
            {"name": "llama2"}
        ]
    }
    mock_response = {
        "response": "Test response"
    }
    with patch('requests.get') as mock_get, \
         patch('ollama.Client') as mock_client:
        mock_get.return_value = MagicMock(status_code=200)
        mock_client.return_value.list.return_value = mock_models
        mock_client.return_value.generate.return_value = mock_response

        client = Ollama()
        response = client.inference("llama2", "Test prompt")
        assert response == "Test response"
        mock_client.return_value.generate.assert_called_once()

def test_ollama_client_inference_invalid_model():
    """Test Ollama client inference with invalid model"""
    mock_models = {
        "models": [
            {"name": "llama2"}
        ]
    }
    with patch('requests.get') as mock_get, \
         patch('ollama.Client') as mock_client:
        mock_get.return_value = MagicMock(status_code=200)
        mock_client.return_value.list.return_value = mock_models

        client = Ollama()
        with pytest.raises(RuntimeError) as exc_info:
            client.inference("invalid-model", "Test prompt")
        assert "Model invalid-model not found" in str(exc_info.value)

def test_ollama_client_inference_server_error():
    """Test Ollama client inference with server error"""
    mock_models = {
        "models": [
            {"name": "llama2"}
        ]
    }
    with patch('requests.get') as mock_get, \
         patch('ollama.Client') as mock_client:
        mock_get.return_value = MagicMock(status_code=200)
        mock_client.return_value.list.return_value = mock_models
        mock_client.return_value.generate.side_effect = Exception("Server error")

        client = Ollama()
        with pytest.raises(RuntimeError) as exc_info:
            client.inference("llama2", "Test prompt")
        assert "Failed to get response from Ollama" in str(exc_info.value)
