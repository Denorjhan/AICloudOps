from agency_swarm.agents import Agent
from agency_swarm.tools import CodeInterpreter
from agency_swarm.tools.coding import ChangeLines, ReadFile, WriteFiles
from AwsSdkAgent.tools import GetAmiId, WriteCode
from ExecutorAgent.tools import ExecutePyCode


class AwsSdkAgent(Agent):
    def __init__(self):
        super().__init__(
            name="AwsSdkAgent",
            description="The AwsSdkAgent specializes in crafting Python scripts for managing AWS services using the boto3 library. This agent's primary role is to generate and modify scripts based on user requirements and feedback from the execution process. It ensures that scripts are optimized, secure, and aligned with best practices, but it does not execute these scripts.",
            instructions="./SOP.md",
            #instructions="./instructions.md",
            tools=[CodeInterpreter, ReadFile, WriteCode],
            model="gpt-3.5-turbo-0125",
        )
