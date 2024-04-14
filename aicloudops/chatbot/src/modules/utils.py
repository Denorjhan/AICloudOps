import os


def display_welcome_message():
    commands = [
        'printf "\n***********************************************************\n" | lolcat',
        'figlet -f slant "AICloudOps" | lolcat',
        'printf "\tYour AI-driven AWS companion!\n" | lolcat',
        'printf "\n***********************************************************\n\n" | lolcat'
    ]
    for command in commands:
        os.system(command)  


# Create a directory for AI-generated code if it doesn't exist
from pathlib import Path

def create_code_directory(directory_name="aicode"):
    current_path = Path.cwd()
    full_path = current_path / directory_name
    if not full_path.exists():
        raise FileNotFoundError(f"Directory '{full_path}' does not exist.")
    return str(full_path)
