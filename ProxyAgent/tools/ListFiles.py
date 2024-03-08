from agency_swarm.tools import BaseTool
from agency_swarm.tools import ToolFactory
from pydantic import Field
import os
import subprocess


class ListFiles(BaseTool):
    """Allows the agent to list the files in a directory."""

    def run(self):
        try:
            result = subprocess.run(
                ['ls'],
                text=True,
                capture_output=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"An error occurred: {e.stderr}"
        
