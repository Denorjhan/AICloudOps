from langchain_community.agent_toolkits import FileManagementToolkit
from agency_swarm.tools import ToolFactory, BaseTool
from pydantic import Field
import os

target_directory = "/Users/denorjhan/Desktop/code/AICloudOps/boto3scripts"
os.chdir(target_directory)

current_directory = os.getcwd()
#scripts_dir = os.path.join(os.getcwd(), 'app/backend/src/scripts') 

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
        #please print out the output of ls[0].run(self) to see the output
        return ls[0].run(self)
    