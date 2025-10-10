"""Tests for the W3M browser implementation."""
import pytest
from unittest.mock import patch, MagicMock
import subprocess
from src.browser.w3m_browser import W3MBrowser

def test_w3m_browser_init():
    """Test W3MBrowser initialization."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        browser = W3MBrowser()
        assert browser.get_current_url() is None
        assert browser.get_current_content() is None
        mock_run.assert_called_once()

def test_w3m_browser_init_failure():
    """Test W3MBrowser initialization failure."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(RuntimeError, match="w3m is not installed"):
            W3MBrowser()

def test_navigate_success():
    """Test successful navigation."""
    with patch('subprocess.run') as mock_run:
        # Mock successful initialization
        mock_run.return_value = MagicMock(returncode=0)
        browser = W3MBrowser()

        # Mock successful navigation
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Test Content"
        )

        success, content = browser.navigate("http://example.com")
        assert success is True
        assert content == "Test Content"
        assert browser.get_current_url() == "http://example.com"
        assert browser.get_current_content() == "Test Content"

def test_navigate_failure():
    """Test navigation failure."""
    with patch('subprocess.run') as mock_run:
        # Mock successful initialization
        mock_run.return_value = MagicMock(returncode=0)
        browser = W3MBrowser()

        # Mock failed navigation
        mock_run.side_effect = subprocess.CalledProcessError(1, 'w3m')

        success, content = browser.navigate("http://invalid.example")
        assert success is False
        assert "Failed to load URL" in content
