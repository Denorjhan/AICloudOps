from agency_swarm.agents import Agent
from agency_swarm.tools import CodeInterpreter
from ProxyAgent.tools import ListDir, ListFiles
import os

class ProxyAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ProxyAgent",
            description="The ProxyAgent serves as the primary interface between users and the AICloudOps system. It interprets user requests, orchestrates the flow of tasks, and communicates with other agents to ensure user needs are met efficiently. This agent is responsible for maintaining clarity in user-agent interactions and ensuring that all necessary information is gathered for task execution.",
            instructions="./instructions.txt",
            files_folder="./files",
            tools=[CodeInterpreter, ListDir],
            #tools_folder="./tools",
            model=os.environ.get("OPENAI_MODEL"),
        )
