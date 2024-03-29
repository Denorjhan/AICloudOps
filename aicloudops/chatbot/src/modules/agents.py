from .config import AI_CONFIG, CODE_WRITER_SYSTEM_MESSAGE
from .docker_exec import ContainerPathDockerExecutor
from autogen import ConversableAgent
from autogen.coding import DockerCommandLineCodeExecutor
from .k8s_exec import K8sCodeExecutor
from .syntax_highlighting_agent import SyntaxHighlightingAgent

# from async_agent import AsyncAgent
# from gui import chat_interface



# Create agent for code execution
def setup_proxy_agent():
    # Setup Docker container for safe code execution
    docker_config = {
        "image": "public.ecr.aws/c6w3t1p6/boto3-code-exec:latest",  # Use a custom boto3 image
        "timeout": 60,
        "auto_remove": True,
        "stop_container": True,
    }
    # execution_container = ContainerPathDockerExecutor(**docker_config)
    k8s_execution_container = K8sCodeExecutor()
    
    proxy_agent = SyntaxHighlightingAgent(
        name="proxy_agent",
        llm_config=AI_CONFIG,  # Disable LLM for code execution agent
        code_execution_config={"executor": k8s_execution_container},  # use DockerCommandLineCodeExecutor when running locally and ContainerPathDockerExecutor when running in a container
        human_input_mode="ALWAYS",
        # chat_interface=chat_interface
    )
    
    return proxy_agent


# Create agent for writing python code
def setup_code_writer_agent():
    
    code_writer_agent = SyntaxHighlightingAgent(
        name="code_writer_agent",
        system_message=CODE_WRITER_SYSTEM_MESSAGE,
        llm_config=AI_CONFIG,
        code_execution_config=False,  # Disable code execution for the code writer agent
    )
    
    return code_writer_agent