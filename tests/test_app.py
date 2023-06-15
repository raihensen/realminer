
"""
To execute the tests please run 'pytest ../tests' from the 'src' folder.
Pytets will execute all the functions with the prefix: 'test_'.
"""
import pytest
import logging
import os
import sys

from unittest.mock import patch
from unittest.mock import MagicMock

# src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
# sys.path.append(src_dir)
import main

# Integration test using pytest

@patch("main.View")
@patch("main.Controller")
def test_basic_app_execution (mock_controller, mock_view):
    """Test the execution of the app without activating the view"""
    
    assert mock_view.called == False
    mock_view.return_value = MagicMock()
    mock_controller.return_value = MagicMock()
    
    app = main.App()

    assert mock_view.call_count == 1
    assert mock_controller.call_count == 1


if __name__ == '__main__':
    pytest.main()