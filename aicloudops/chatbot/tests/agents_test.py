import pytest
from unittest.mock import patch, MagicMock
from src.agents import setup_proxy_agent, setup_code_writer_agent
from src.ai_cloud_ops_conversable_agent import AiCloudOpsConversableAgent
from src.config import AI_CONFIG, CODE_WRITER_SYSTEM_MESSAGE


# Parameters for the test include each key in the dictionary and the corresponding executor class
@pytest.mark.parametrize(
    "env, executor_class",
    [
        ("docker", "DockerCodeExecutor"),
        ("k8s", "K8sCodeExecutor"),
        ("local", "DockerCommandLineCodeExecutor"),
    ],
)
def test_valid_execution_env(env, executor_class):
    # Patch the specific executor class to be used in this test
    with patch.dict("os.environ", {"RUNNING_IN": env}), patch(
        "kubernetes.config.load_incluster_config", return_value=MagicMock()
    ):
        agent = setup_proxy_agent()

        # Ensure the correct executor instance in the agent's configuration
        assert agent.__class__.__name__ == AiCloudOpsConversableAgent.__name__
        assert agent.name == "proxy_agent"
        assert agent.llm_config == AI_CONFIG
        assert (
            agent._code_execution_config["executor"].__class__.__name__
            == executor_class
        )
        assert agent.human_input_mode == "ALWAYS"


# test invalid execution env
def test_invalid_execution_env():
    with patch("os.environ", {"RUNNING_IN": "invalid_env"}):
        with pytest.raises(Exception):
            setup_proxy_agent()


@pytest.mark.parametrize(
    "env",
    [
        "doCkEr",
        "k8S",
        "lOcAl",
    ],
)
def test_proxy_agent_creation(env):
    with patch.dict("os.environ", {"RUNNING_IN": env}), patch(
        "kubernetes.config.load_incluster_config", return_value=MagicMock()
    ):
        agent = setup_proxy_agent()

        # Ensure the correct executor instance in the agent's configuration
        assert agent.__class__.__name__ == AiCloudOpsConversableAgent.__name__
        assert agent.name == "proxy_agent"
        assert agent.llm_config == AI_CONFIG
        assert agent.human_input_mode == "ALWAYS"


# test code writer agent creation
def test_code_writer_agent_creation():
    agent = setup_code_writer_agent()
    assert agent.__class__.__name__ == AiCloudOpsConversableAgent.__name__
    assert agent.name == "code_writer_agent"
    assert agent.system_message == CODE_WRITER_SYSTEM_MESSAGE
    assert agent.llm_config == AI_CONFIG
    assert agent._code_execution_config == False
