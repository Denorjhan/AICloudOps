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
def create_code_directory(directory_name="aicode"):
    current_path = os.getcwd()
    full_path = os.path.join(current_path, directory_name)
    if not os.path.exists(full_path):
        raise OSError(f"Directory '{full_path}' does not exists.")
    return full_path