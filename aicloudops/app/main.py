import os
from modules.utils import create_code_directory, display_welcome_message
from modules.agents import setup_proxy_agent, setup_code_writer_agent
# import autogen.runtime_logging


def main():

    display_welcome_message()
    

    # Init agents
    
    # logging_session_id = autogen.runtime_logging.start(logger_type="sqlite", config={"dbname": "l100.db"})
    # print("Logging session ID: " + str(logging_session_id))
    proxy_agent = setup_proxy_agent()
    
    code_writer_agent = setup_code_writer_agent()

    # autogen.runtime_logging.stop()

    # Get user input
    prompt2 = input("enter your prompt:")
    
    chat_result = proxy_agent.initiate_chat(code_writer_agent, message=prompt2)
    
    

if __name__ == "__main__":
    main()
    