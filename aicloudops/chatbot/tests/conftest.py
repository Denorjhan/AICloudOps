import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_proxy_agent():
    return MagicMock()


@pytest.fixture
def mock_code_writer_agent():
    return MagicMock()

