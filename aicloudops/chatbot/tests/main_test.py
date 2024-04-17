import pytest
from unittest.mock import patch
from src.main import main


def test_main_initialization(mock_proxy_agent, mock_code_writer_agent):
    prompt = "Test prompt"
    with patch(
        "src.main.setup_proxy_agent", return_value=mock_proxy_agent
    ) as mock_setup_proxy, patch(
        "src.main.setup_code_writer_agent", return_value=mock_code_writer_agent
    ) as mock_setup_writer, patch(
        "src.main.display_welcome_message"
    ) as mock_welcome, patch("builtins.input", return_value=prompt):
        main()

        mock_welcome.assert_called_once()
        mock_setup_proxy.assert_called_once()
        mock_setup_writer.assert_called_once()
        mock_proxy_agent.initiate_chat.assert_called_once_with(
            mock_code_writer_agent, message=prompt
        )
