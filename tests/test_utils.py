import pytest
import time
import requests
from unittest.mock import Mock, patch
from src.services.utils import retry_wrapper

def test_retry_wrapper_rate_limit():
    # Mock a function that raises rate limit error
    @retry_wrapper
    def rate_limited_func():
        response = Mock(spec=requests.Response)
        response.status_code = 429
        response.json.return_value = {
            'error': {
                'message': 'Rate limit reached',
                'type': 'tokens',
                'code': 'rate_limit_exceeded'
            }
        }
        raise requests.exceptions.HTTPError(response=response)

    # Test that it waits 60 seconds on rate limit
    with patch('time.sleep') as mock_sleep:
        with pytest.raises(requests.exceptions.HTTPError):
            rate_limited_func()
        # Verify it attempted to sleep for 60 seconds
        assert mock_sleep.call_args[0][0] == 60

def test_retry_wrapper_other_errors():
    # Mock a function that raises other HTTP errors
    @retry_wrapper
    def other_error_func():
        response = Mock(spec=requests.Response)
        response.status_code = 500
        raise requests.exceptions.HTTPError(response=response)

    # Test that it retries with default backoff
    with patch('time.sleep') as mock_sleep:
        with pytest.raises(requests.exceptions.HTTPError):
            other_error_func()
        # Verify it used shorter retry delays
        assert all(call[0][0] < 60 for call in mock_sleep.call_args_list)
