"""
ASCII-based browser implementation using w3m.

This module provides a lightweight terminal-based browser implementation
using w3m for web access without requiring expensive API calls or screenshots.
"""
import subprocess
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class W3MBrowser:
    """Terminal-based browser using w3m."""

    def __init__(self):
        """Initialize the W3M browser wrapper."""
        self._verify_w3m_installation()
        self.current_url: Optional[str] = None
        self.current_content: Optional[str] = None

    def _verify_w3m_installation(self) -> None:
        """Verify w3m is installed and accessible."""
        try:
            subprocess.run(['w3m', '-version'],
                         check=True,
                         capture_output=True,
                         text=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError("w3m is not installed or not accessible") from e

    def navigate(self, url: str) -> Tuple[bool, str]:
        """Navigate to a URL and return the page content in ASCII format."""
        self.current_url = url
        try:
            result = subprocess.run(
                ['w3m', '-dump', url],
                check=True,
                capture_output=True,
                text=True
            )
            self.current_content = result.stdout
            return True, self.current_content
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to load URL {url}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_current_content(self) -> Optional[str]:
        """Get the current page content."""
        return self.current_content

    def get_current_url(self) -> Optional[str]:
        """Get the current URL."""
        return self.current_url
