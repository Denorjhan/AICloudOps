from .config import AI_CONFIG, CODE_WRITER_SYSTEM_MESSAGE
from .docker_exec import ContainerPathDockerExecutor
from autogen import ConversableAgent
from autogen.coding import DockerCommandLineCodeExecutor


# Create agent for code execution
def setup_proxy_agent():
    # Setup Docker container for safe code execution
    docker_config = {
        "image": "boto3",  # Use a custom boto3 image
        "timeout": 60,
        "auto_remove": True,
        "stop_container": True,
    }
    execution_container = ContainerPathDockerExecutor(**docker_config)
    
    proxy_agent = ConversableAgent(
        name="proxy_agent",
        llm_config=AI_CONFIG,  # Disable LLM for code execution agent
        code_execution_config={"executor": execution_container},  # use DockerCommandLineCodeExecutor when running locally and ContainerPathDockerExecutor when running in a container
        human_input_mode="ALWAYS",
    )
    
    return proxy_agent


# Create agent for writing python code
def setup_code_writer_agent():
    
    code_writer_agent = ConversableAgent(
        name="code_writer_agent",
        system_message=CODE_WRITER_SYSTEM_MESSAGE,
        llm_config=AI_CONFIG,
        code_execution_config=False,  # Disable code execution for the code writer agent
    )
    
    return code_writer_agent