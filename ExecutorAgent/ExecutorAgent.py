from agency_swarm.agents import Agent
from agency_swarm.tools import CodeInterpreter
from agency_swarm.tools.coding import ChangeLines, ReadFile, WriteFiles
from ExecutorAgent.tools import ExecutePyCode, CodeValidation, InLineEdit
from ProxyAgent.tools import ListDir


class ExecutorAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ExecutorAgent",
            description="The ExecutorAgent is responsible for validating and executing the scripts created by the AwsSdkAgent. It checks scripts for errors, runs them to perform the desired AWS operations, and provides feedback in case of issues. This agent is key to ensuring that the scripts not only meet the user's specifications but also execute successfully within the AWS environment.",
            instructions="./instructions.md",
            tools=[CodeInterpreter, ReadFile, ExecutePyCode, CodeValidation, ListDir],
            model="gpt-3.5-turbo-0125",
        )

        # change writefiles to a custom change lines so it csnt create an entire new file
        # might need listDir to get the file path if we are not going to pass it in the messages