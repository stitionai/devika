"""
Tests for sandbox security implementation.
"""
import pytest
from src.sandbox.code_runner import CodeRunner
from src.sandbox.firejail import Sandbox

def test_restricted_imports():
    runner = CodeRunner()
    code = """
import os
os.system('echo "test"')
"""
    result = runner.run(code)
    assert not result["success"]
    assert "restricted import" in result["error"].lower()

def test_restricted_calls():
    runner = CodeRunner()
    code = """
eval('print("test")')
"""
    result = runner.run(code)
    assert not result["success"]
    assert "restricted function call" in result["error"].lower()

def test_safe_code_execution():
    runner = CodeRunner()
    code = """
print("Hello, World!")
"""
    result = runner.run(code)
    assert result["success"]
    assert "Hello, World!" in result["output"]

def test_timeout():
    runner = CodeRunner()
    code = """
while True:
    pass
"""
    result = runner.run(code, timeout=1)
    assert not result["success"]
    assert "timeout" in result["error"].lower()

def test_sandbox_profile():
    sandbox = Sandbox()
    with pytest.raises(RuntimeError):
        # Should fail when trying to access network
        code = """
import urllib.request
urllib.request.urlopen('http://example.com')
"""
        sandbox.run_code(code)
