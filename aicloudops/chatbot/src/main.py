from utils import display_welcome_message
from agents import setup_proxy_agent, setup_code_writer_agent


def main():
    display_welcome_message()
    proxy_agent = setup_proxy_agent()
    code_writer_agent = setup_code_writer_agent()
    user_prompt = input("EnterY our Prompt: ")
    proxy_agent.initiate_chat(code_writer_agent, message=user_prompt)


if __name__ == "__main__":
    main()
