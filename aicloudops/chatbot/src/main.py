import os
from modules.utils import create_code_directory, display_welcome_message
from modules.agents import setup_proxy_agent, setup_code_writer_agent



def main():
    display_welcome_message()
    proxy_agent = setup_proxy_agent()
    code_writer_agent = setup_code_writer_agent()
    prompt2 = input("enter your prompt:")
    chat_result = proxy_agent.initiate_chat(code_writer_agent, message=prompt2)
if __name__ == "__main__":
    main()

