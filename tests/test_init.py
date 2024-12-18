import pytest
from unittest.mock import patch
import numpy

def test_numpy_import():
    """Test that numpy can be imported and has correct version."""
    assert numpy.__version__ >= "1.24.0"

def test_init_devika_numpy_validation():
    """Test that init_devika validates numpy dependency."""
    from src.init import init_devika

    # Should not raise any ImportError
    init_devika()

@patch("importlib.import_module")
def test_init_devika_numpy_missing(mock_import):
    """Test that init_devika handles missing numpy correctly."""
    mock_import.side_effect = ImportError("No module named numpy")

    with pytest.raises(ImportError) as exc_info:
        from src.init import init_devika
        init_devika()

    assert "numpy is required but not installed" in str(exc_info.value)
