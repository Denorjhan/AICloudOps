import subprocess
import tempfile
from typing import Union, Dict, List
from autogen.agentchat.conversable_agent import ConversableAgent, Agent
from autogen.oai.client import OpenAIWrapper
from termcolor import colored
from autogen.coding.markdown_code_extractor import MarkdownCodeExtractor, CodeBlock


class CustomConversableAgent(ConversableAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_extractor = MarkdownCodeExtractor()

    def _print_received_message(self, message: Union[Dict, str], sender: Agent):
        print(colored(sender.name, "yellow"), "(to", f"{self.name}):\n", flush=True)
        message = self._message_to_dict(message)

        
        content = message.get("content")
        content = OpenAIWrapper.instantiate(
            content,
            message["content"],
            self.llm_config and self.llm_config.get("allow_format_str_template", False),
        )
        # Extract and print any code blocks found in the content
        code_blocks = self.code_extractor.extract_code_blocks(content)
        if code_blocks:
            for code_block in code_blocks:
                self._print_with_bat(code_block.code)
        else:
            print(content)

        print("\n", "-" * 80, flush=True, sep="")

    def _print_with_bat(self, content: str):
        with tempfile.NamedTemporaryFile("w", delete=True) as tmpfile:
            tmpfile.write(content)
            tmpfile.flush()
            subprocess.run(["bat", "--style=numbers,changes,grid", "--color=always", "--language=python", "--paging=never", tmpfile.name])

    def _message_to_dict(self, message: Union[Dict, str]) -> Dict:
        return message if isinstance(message, Dict) else {"content": message}
    
    def get_human_input(self, prompt: str) -> str:
            """Get human input.

            Override this method to customize the way to get human input.

            Args:
                prompt (str): prompt for the human input.

            Returns:
                str: human input.
            """
            # f"Please give feedback to {sender_name}. Press enter or type 'exit' to stop the conversation: "
            msg = "Please provide feedback to the Code Writer Agent or press ENTER to execute the code or type 'exit' to stop the conversation: "
            reply = input(msg) 
            self._human_input.append(reply)
            return reply
