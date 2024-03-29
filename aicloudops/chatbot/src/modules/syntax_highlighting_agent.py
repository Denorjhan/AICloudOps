import subprocess
import tempfile
from typing import Union, Dict
from autogen.agentchat.conversable_agent import ConversableAgent, Agent
from autogen.oai.client import OpenAIWrapper
from termcolor import colored

class SyntaxHighlightingAgent(ConversableAgent):
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
            self._print_with_bat(message["content"])
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
                self._print_with_bat(content)

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
        with tempfile.NamedTemporaryFile("w", delete=False) as tmpfile:
            tmpfile.write(content)
            tmpfile.flush()
            subprocess.run(["bat", "--paging=never", tmpfile.name])