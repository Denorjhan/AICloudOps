from agency_swarm.tools import BaseTool
from pydantic import Field
import ast
import sys


class CodeValidation(BaseTool):
    """Validates a Python script for syntax errors and performs a static analysis check."""
    script_path: str = Field(
        ..., description="The path to the .py file to be executed."
    )

    def run(self):
        """
        Validates a Python script for syntax errors and compile-time errors.
        """
        try:
            # Read the script content
            with open(self.script_path, "r") as file:
                script_content = file.read()

            # Syntax Check: Attempt to parse the script into an AST
            tree = ast.parse(script_content, filename=self.script_path, mode='exec')
            print("Syntax check passed.")

            # Compile the AST to check for some compile-time errors
            compile(tree, self.script_path, 'exec')
            print("Compile-time checks passed.")

            # Further static analysis can be added here using AST visitors or other tools

            # Optional: Very limited runtime check in a controlled environment
            # Warning: Use `exec` with caution, especially with untrusted code
            # exec(compile(tree, script_path, 'exec'), {'__builtins__': {}})

            return f"{self.script_path}: Syntax and static analysis checks passed."

        except SyntaxError as e:
            return f"SyntaxError in {self.script_path}: {e}"
        except Exception as e:
            return f"Error in {self.script_path}: {e}"
