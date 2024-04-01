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

        if message.get("tool_responses"):
            for tool_response in message["tool_responses"]:
                self._print_received_message(tool_response, sender)
            if message.get("role") == "tool":
                return

        if message.get("role") in ["function", "tool"]:
            id_key = "name" if message["role"] == "function" else "tool_call_id"
            func_print = f"***** Response from calling {message['role']} \"{message[id_key]}\" *****"
            print(colored(func_print, "green"), flush=True)
            # Extract and print code blocks using bat
            code_blocks = self.code_extractor.extract_code_blocks(message["content"])
            for code_block in code_blocks:
                self._print_with_bat(code_block.code)
            print(colored("*" * len(func_print), "green"), flush=True)
        else:
            content = message.get("content")
            if content is not None:
                if "context" in message:
                    content = OpenAIWrapper.instantiate(
                        content,
                        message["context"],
                        self.llm_config and self.llm_config.get("allow_format_str_template", False),
                    )
                # Extract and print code blocks using bat
                code_blocks = self.code_extractor.extract_code_blocks(content)
                if code_blocks:
                    for code_block in code_blocks:
                        self._print_with_bat(code_block.code)
                else:
                    print(content)

            if "function_call" in message and message["function_call"]:
                function_call = dict(message["function_call"])
                func_print = f"***** Suggested function Call: {function_call.get('name', '(No function name found)')} *****"
                print(colored(func_print, "green"), flush=True)
                print("Arguments: \n", function_call.get("arguments", "(No arguments found)"), flush=True, sep="")
                print(colored("*" * len(func_print), "green"), flush=True)

            if "tool_calls" in message and message["tool_calls"]:
                for tool_call in message["tool_calls"]:
                    id = tool_call.get("id", "(No id found)")
                    function_call = dict(tool_call.get("function", {}))
                    func_print = f"***** Suggested tool Call ({id}): {function_call.get('name', '(No function name found)')} *****"
                    print(colored(func_print, "green"), flush=True)
                    print("Arguments: \n", function_call.get("arguments", "(No arguments found)"), flush=True, sep="")
                    print(colored("*" * len(func_print), "green"), flush=True)

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
            msg = "Please give feedback to the CodeWriterAgent. Press ENTER to execute the code or type 'exit' to stop the conversation: "
            reply = input(msg)
            self._human_input.append(reply)
            return reply
