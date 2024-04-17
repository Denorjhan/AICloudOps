import os
from config import AI_CONFIG, CODE_WRITER_SYSTEM_MESSAGE
from docker_code_executor import DockerCodeExecutor
from k8s_code_executor import K8sCodeExecutor
from ai_cloud_ops_conversable_agent import AiCloudOpsConversableAgent
from autogen.coding import DockerCommandLineCodeExecutor


# Create agent for code execution
def setup_proxy_agent():
    # Lookup dictionary
    EXECUTION_ENVIRONMENTS = {
        "docker": DockerCodeExecutor,
        "k8s": K8sCodeExecutor,
        "local": DockerCommandLineCodeExecutor,
    }

    try:
        execution_env = EXECUTION_ENVIRONMENTS.get(
            os.getenv("RUNNING_IN", "local").lower()
        )
    except Exception as e:
        print(f"Error setting up code execution container: {e}\n \
            please provide a valid value for RUNNING_IN environment variable")

    proxy_agent = AiCloudOpsConversableAgent(
        name="proxy_agent",
        llm_config=AI_CONFIG,
        code_execution_config={"executor": execution_env()},
        human_input_mode="ALWAYS",
    )

    return proxy_agent


# Create agent for writing python code
def setup_code_writer_agent():
    code_writer_agent = AiCloudOpsConversableAgent(
        name="code_writer_agent",
        system_message=CODE_WRITER_SYSTEM_MESSAGE,
        llm_config=AI_CONFIG,
        code_execution_config=False,  # Disable code execution for the code writer agent
    )

    return code_writer_agent
