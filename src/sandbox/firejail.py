"""
Firejail-based sandbox for secure code execution.
"""
import subprocess
import os
import tempfile
import shutil
from typing import Dict, List, Optional, Tuple

class Sandbox:
    """
    Provides a secure sandbox environment for code execution using firejail.
    """

    def __init__(self):
        self._verify_firejail()

    def _verify_firejail(self):
        """Verify firejail is installed."""
        try:
            subprocess.run(['which', 'firejail'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise RuntimeError("Firejail is not installed. Please install it using: sudo apt-get install firejail")

    def create_sandbox_profile(self, temp_dir: str) -> str:
        """Create a restrictive firejail profile."""
        profile_content = """
# Firejail profile for code execution
include /etc/firejail/disable-common.inc
include /etc/firejail/disable-programs.inc

# Basic filesystem restrictions
whitelist ${HOME}
private-bin python3,python,pip
private-dev
private-tmp

# Networking restrictions
net none

# Further restrictions
caps.drop all
nonewprivs
noroot
seccomp
"""
        profile_path = os.path.join(temp_dir, "sandbox.profile")
        with open(profile_path, "w") as f:
            f.write(profile_content)
        return profile_path

    def run_code(self, code: str, timeout: int = 30) -> Tuple[str, str, int]:
        """
        Run code in a sandboxed environment.

        Args:
            code: The Python code to execute
            timeout: Maximum execution time in seconds

        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create code file
            code_path = os.path.join(temp_dir, "code.py")
            with open(code_path, "w") as f:
                f.write(code)

            # Create sandbox profile
            profile_path = self.create_sandbox_profile(temp_dir)

            # Run code in sandbox
            try:
                result = subprocess.run(
                    [
                        'firejail',
                        f'--profile={profile_path}',
                        '--quiet',
                        'python3',
                        code_path
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                    text=True
                )
                return result.stdout, result.stderr, result.returncode
            except subprocess.TimeoutExpired:
                return "", "Code execution timed out", 1
            except Exception as e:
                return "", f"Error executing code: {str(e)}", 1
