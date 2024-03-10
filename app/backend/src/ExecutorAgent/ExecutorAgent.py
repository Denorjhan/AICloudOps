from agency_swarm.agents import Agent
from agency_swarm.tools import CodeInterpreter
from agency_swarm.tools.coding import ChangeLines, ReadFile, WriteFiles
from ExecutorAgent.tools import ExecutePyCode, CodeValidation, InLineEdit
from ProxyAgent.tools import ListDir
import os


class ExecutorAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ExecutorAgent",
            description="The ExecutorAgent is responsible for validating and executing the scripts created by the AwsSdkAgent. It checks scripts for errors, runs them to perform the desired AWS operations, and provides feedback in case of issues. This agent is key to ensuring that the scripts not only meet the user's specifications but also execute successfully within the AWS environment.",
            instructions="./instructions.md",
            tools=[CodeInterpreter, ReadFile, ExecutePyCode, CodeValidation, ListDir],
            model=os.environ.get("OPENAI_MODEL"),
        )

        # add debug tool that reads the output of execution and determines a plan of action on how to fix it