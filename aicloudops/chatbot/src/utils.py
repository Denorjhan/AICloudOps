import os
from pathlib import Path
from typing import List
import uuid
from hashlib import md5
from autogen.coding.base import CodeBlock
from autogen.coding.base import CommandLineCodeResult
from autogen.coding.utils import _get_file_name_from_content
import json


def display_welcome_message():
    commands = [
        'printf "\n***********************************************************\n" | lolcat',
        'figlet -f slant "AICloudOps" | lolcat',
        'printf "\tYour AI-driven AWS companion!\n" | lolcat',
        'printf "\n***********************************************************\n\n" | lolcat',
    ]
    for command in commands:
        os.system(command)


def create_code_directory(directory_name="aicode"):
    current_path = Path.cwd()
    full_path = current_path / directory_name
    if not full_path.exists():
        raise FileNotFoundError(f"Directory '{full_path}' does not exist.")
    return str(full_path)


def code_block_to_file(code_block: CodeBlock, work_dir: Path) -> str:
    lang = code_block.language
    code = code_block.code

    try:
        # Check if there is a filename comment
        filename = _get_file_name_from_content(code, Path("/tmp"))
    except ValueError:
        return CommandLineCodeResult(
            exit_code=1, output="Filename is not in the workspace"
        )

    if filename is None:
        # Create a file with an automatically generated name
        code_hash = md5(code.encode()).hexdigest()
        filename = f"tmp_code_{code_hash}.{'py' if lang.startswith('python') else lang}"
    else:
        filename = f"{filename.removesuffix('.py')}_{uuid.uuid4()}.py"

    code_path = work_dir / filename
    code_path.write_text(code)

    return str(code_path)


def validate_code_blocks(code_blocks: List[CodeBlock]):
    if not code_blocks:
        raise ValueError("No code blocks to execute.")
    elif len(code_blocks) > 1:
        print("Can only execute one code block at a time. Executing the first block...")


def create_msg_body(file_path: str, exit_code: int, output: str) -> str:
    body_dict = {"file_path": file_path, "exit_code": exit_code, "output": output}
    body_json = json.dumps(body_dict)
    return body_json
