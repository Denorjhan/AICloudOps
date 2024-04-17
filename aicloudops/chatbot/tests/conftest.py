import pytest
from unittest.mock import MagicMock

import sys
import os

# def pytest_configure():
#     sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
#     print(sys.path[0])


@pytest.fixture
def mock_proxy_agent():
    return MagicMock()


@pytest.fixture
def mock_code_writer_agent():
    return MagicMock()
