import os
import pytest
from src.config import Config

@pytest.fixture
def config():
    # Create a temporary config for testing
    if os.path.exists("config.toml"):
        os.rename("config.toml", "config.toml.bak")

    yield Config()

    # Restore original config
    if os.path.exists("config.toml.bak"):
        os.rename("config.toml.bak", "config.toml")
    else:
        os.remove("config.toml")

def test_excluded_sites_empty_by_default(config):
    """Test that excluded sites list is empty by default."""
    assert config.get_excluded_sites() == []

def test_set_excluded_sites(config):
    """Test setting and getting excluded sites."""
    test_sites = ["example.com", "test.org"]
    config.set_excluded_sites(test_sites)
    assert config.get_excluded_sites() == test_sites

def test_excluded_sites_persistence(config):
    """Test that excluded sites persist after saving."""
    test_sites = ["example.com", "test.org"]
    config.set_excluded_sites(test_sites)

    # Create new config instance to test persistence
    new_config = Config()
    assert new_config.get_excluded_sites() == test_sites

def test_update_excluded_sites(config):
    """Test updating excluded sites list."""
    initial_sites = ["example.com"]
    config.set_excluded_sites(initial_sites)

    updated_sites = ["example.com", "test.org"]
    config.set_excluded_sites(updated_sites)
    assert config.get_excluded_sites() == updated_sites
