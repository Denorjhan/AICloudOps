from agency_swarm.tools import BaseTool
from pydantic import Field
import subprocess

class ExecutePyCode(BaseTool):
    """Run existing python file from local disc."""
    file_name: str = Field(
        ..., description="The path to the .py file to be executed."
    )

    def run(self):
        print(self.file_name)
        """Executes a Python script at the given file path and captures its output and errors."""
        try:
            result = subprocess.run(
                ['python3', self.file_name],
                text=True,
                capture_output=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"An error occurred: {e.stderr}"
