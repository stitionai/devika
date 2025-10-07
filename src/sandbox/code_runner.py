"""
Code execution manager with security restrictions.
"""
from typing import Dict, Optional, Tuple
import os
import re
from .firejail import Sandbox

class CodeRunner:
    """
    Manages secure code execution with restrictions and validation.
    """

    # Restricted imports that could be dangerous
    RESTRICTED_IMPORTS = {
        'os.system', 'subprocess', 'pty', 'socket', 'requests',
        'urllib', 'ftplib', 'telnetlib', 'smtplib'
    }

    # Restricted function calls
    RESTRICTED_CALLS = {
        r'eval\s*\(', r'exec\s*\(', r'open\s*\(',
        r'__import__\s*\(', r'globals\s*\(', r'locals\s*\('
    }

    def __init__(self):
        self.sandbox = Sandbox()

    def validate_code(self, code: str) -> Tuple[bool, str]:
        """
        Validate code for security concerns.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for restricted imports
        for imp in self.RESTRICTED_IMPORTS:
            if imp in code:
                return False, f"Use of restricted import: {imp}"

        # Check for restricted function calls
        for call in self.RESTRICTED_CALLS:
            if re.search(call, code):
                return False, f"Use of restricted function call pattern: {call}"

        return True, ""

    def run(self, code: str, timeout: int = 30) -> Dict[str, str]:
        """
        Run code securely with validation and sandboxing.

        Args:
            code: The Python code to execute
            timeout: Maximum execution time in seconds

        Returns:
            Dict containing execution results
        """
        # Validate code
        is_valid, error = self.validate_code(code)
        if not is_valid:
            return {
                "success": False,
                "error": error,
                "output": "",
            }

        # Run in sandbox
        stdout, stderr, return_code = self.sandbox.run_code(code, timeout)

        return {
            "success": return_code == 0,
            "output": stdout,
            "error": stderr if stderr else "",
        }
