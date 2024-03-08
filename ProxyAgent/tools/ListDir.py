from langchain_community.agent_toolkits import FileManagementToolkit
from agency_swarm.tools import ToolFactory, BaseTool
from pydantic import Field
import os

current_directory = os.getcwd()

# Get the list_directory tool from the FileManagementToolkit. 
langchain_tool = FileManagementToolkit(
root_dir=str(current_directory),
selected_tools=["list_directory"],
).get_tools()

# Convert langchain tool to a BaseTool
ls = ToolFactory.from_langchain_tools(langchain_tool)


class ListDir (BaseTool):
    """Return a list of files in the current directory"""

    def run(self):
        return ls[0].run(self)
    

