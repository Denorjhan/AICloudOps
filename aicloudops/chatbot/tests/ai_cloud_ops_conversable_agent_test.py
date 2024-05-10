import pytest
from unittest.mock import patch, MagicMock
from src.ai_cloud_ops_conversable_agent import AiCloudOpsConversableAgent
from autogen.agentchat.conversable_agent import Agent
from autogen.coding.markdown_code_extractor import MarkdownCodeExtractor
from autogen.coding import DockerCommandLineCodeExecutor
import subprocess


@pytest.fixture
def agent():
    return AiCloudOpsConversableAgent(
        name="Receiving Agent",
        code_execution_config={"executor": DockerCommandLineCodeExecutor()},
    )


@pytest.fixture
def sender():
    sender = MagicMock(spec=Agent)
    sender.name = "Test Sender"
    return sender


def test_init(agent):
    assert isinstance(agent.code_extractor, MarkdownCodeExtractor)


@patch("builtins.print")
def test_print_received_message(mock_print, agent, sender):
    message = {"content": "Test message"}
    with patch.object(agent, "_print_with_bat") as mock_print_with_bat:
        agent._print_received_message(message, sender)
        mock_print.assert_any_call(
            "Test Sender", "(to", "Receiving Agent):\n", flush=True
        )
        mock_print_with_bat.assert_not_called()
        mock_print.assert_called_with("\n", "-" * 80, flush=True, sep="")


@patch("builtins.print")
def test_print_received_message_with_code_blocks(mock_print, agent, sender):
    message = {"content": "```python\nprint('Hello, World!')\n```"}
    with patch.object(agent, "_print_with_bat") as mock_print_with_bat:
        agent._print_received_message(message, sender)
        mock_print.assert_any_call(
            "Test Sender", "(to", "Receiving Agent):\n", flush=True
        )
        mock_print_with_bat.assert_called_once_with("print('Hello, World!')")
        mock_print.assert_called_with("\n", "-" * 80, flush=True, sep="")


@patch("subprocess.Popen")
def test_print_with_bat(mock_popen, agent):
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    content = "print('Hello, World!')"
    agent._print_with_bat(content)
    mock_popen.assert_called_once_with(
        [
            "bat",
            "--style=numbers,changes,grid",
            "--color=always",
            "--language=python",
            "--paging=never",
        ],
        stdin=subprocess.PIPE,
    )
    mock_process.communicate.assert_called_once_with(input=content.encode())


def test_message_to_dict(agent):
    message_dict = {"content": "Test message"}
    assert agent._message_to_dict(message_dict) == message_dict
    message_str = "Test message"
    assert agent._message_to_dict(message_str) == {"content": message_str}


@patch("builtins.input", return_value="Test feedback")
def test_get_human_input(mock_input, agent):
    prompt = "Please provide feedback"
    feedback = agent.get_human_input(prompt)
    assert feedback == "Test feedback"
    assert agent._human_input[-1] == "Test feedback"


def test_generate_code_execution_reply_using_executor_invalid_config(agent):
    with pytest.raises(ValueError, match="config is not supported"):
        agent._generate_code_execution_reply_using_executor(config={})


def test_generate_code_execution_reply_using_executor_code_execution_disabled(agent):
    agent._code_execution_config = False
    assert agent._generate_code_execution_reply_using_executor() == (False, None)


def test_generate_code_execution_reply_using_executor_auto_last_n_messages(agent):
    messages = [
        {"role": "system", "content": "System message"},
        {"role": "user", "content": "User message 1"},
        {"role": "assistant", "content": "Assistant message"},
        {"role": "user", "content": "User message 2"},
    ]
    with patch.object(
        agent.code_executor, "execute_code_blocks", return_value=[]
    ) as mock_execute_code_blocks:
        is_success, summary = agent._generate_code_execution_reply_using_executor(
            messages
        )
        assert is_success is False
        assert summary is None
        assert mock_execute_code_blocks.call_count == 0


def test_generate_code_execution_reply_using_executor_no_code_blocks(agent):
    messages = [{"content": "Message without code blocks"}]
    with patch.object(
        agent.code_executor, "execute_code_blocks", return_value=[]
    ) as mock_execute_code_blocks:
        is_success, summary = agent._generate_code_execution_reply_using_executor(
            messages
        )
        assert is_success is False
        assert summary is None
        assert mock_execute_code_blocks.call_count == 0


def test_generate_code_execution_reply_using_executor_successful_execution(agent):
    messages = [{"content": "```python\nprint('Hello, World!')\n```"}]
    code_result = MagicMock(exit_code=0, output="Hello, World!")
    with patch.object(
        agent.code_executor, "execute_code_blocks", return_value=[code_result]
    ) as mock_execute_code_blocks:
        is_success, summary = agent._generate_code_execution_reply_using_executor(
            messages
        )
        assert is_success is True
        assert "All code blocks executed successfully" in summary
        assert "exitcode: 0 (execution succeeded)" in summary
        assert "Code output: \nHello, World!" in summary
        assert mock_execute_code_blocks.call_count == 1


def test_generate_code_execution_reply_using_executor_failed_execution(agent):
    messages = [{"content": "```python\nraise Exception('Error')\n```"}]
    code_result = MagicMock(
        exit_code=1,
        output='Traceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nException: Error',
    )
    with patch.object(
        agent.code_executor, "execute_code_blocks", return_value=[code_result]
    ) as mock_execute_code_blocks:
        is_success, summary = agent._generate_code_execution_reply_using_executor(
            messages
        )
        assert is_success is False
