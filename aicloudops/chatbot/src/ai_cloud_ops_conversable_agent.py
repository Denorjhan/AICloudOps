import subprocess
from typing import Union, Dict
from autogen.agentchat.conversable_agent import ConversableAgent, Agent
from autogen.oai.client import OpenAIWrapper
from termcolor import colored
from autogen.coding.markdown_code_extractor import MarkdownCodeExtractor
from typing import Optional, Literal, List


class AiCloudOpsConversableAgent(ConversableAgent):
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
        process = subprocess.Popen(
            [
                "bat",
                "--style=numbers,changes,grid",
                "--color=always",
                "--language=python",
                "--paging=never",
            ],
            stdin=subprocess.PIPE,
        )
        process.communicate(input=content.encode())

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

    def _generate_code_execution_reply_using_executor(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Union[Dict, Literal[False]]] = None,
    ):
        """Generate a reply using code executor."""
        if config is not None:
            raise ValueError(
                "config is not supported for _generate_code_execution_reply_using_executor."
            )
        if self._code_execution_config is False:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]
        last_n_messages = self._code_execution_config.get("last_n_messages", "auto")

        if (
            not (isinstance(last_n_messages, (int, float)) and last_n_messages >= 0)
            and last_n_messages != "auto"
        ):
            raise ValueError(
                "last_n_messages must be either a non-negative integer, or the string 'auto'."
            )

        num_messages_to_scan = last_n_messages
        if last_n_messages == "auto":
            # Find when the agent last spoke
            num_messages_to_scan = 0
            for message in reversed(messages):
                if "role" not in message:
                    break
                elif message["role"] != "user":
                    break
                else:
                    num_messages_to_scan += 1
        num_messages_to_scan = min(len(messages), num_messages_to_scan)
        messages_to_scan = messages[-num_messages_to_scan:]

        summary = None
        is_success = False

        print("################")
        # iterate through the last n messages in reverse
        # if code blocks are found, execute the code blocks and return the output
        # if no code blocks are found, continue
        for message in reversed(messages_to_scan):
            print(message)
            if not message["content"]:
                continue
            print(self._code_executor.code_extractor, "\nexec:", self._code_executor)
            code_blocks = self._code_executor.code_extractor.extract_code_blocks(
                message["content"]
            )
            print(len(code_blocks))
            if len(code_blocks) == 0:
                continue

            num_code_blocks = len(code_blocks)
            if num_code_blocks == 1:
                print(
                    colored(
                        f"\n>>>>>>>> EXECUTING CODE BLOCK (inferred language is {code_blocks[0].language})...",
                        "red",
                    ),
                    flush=True,
                )
            else:
                print(
                    colored(
                        f"\n>>>>>>>> EXECUTING {num_code_blocks} CODE BLOCKS (inferred languages are [{', '.join([x.language for x in code_blocks])}])...",
                        "red",
                    ),
                    flush=True,
                )

            # found code blocks, execute code.
            code_results = self._code_executor.execute_code_blocks(code_blocks)
            exit_codes = [code_result.exit_code for code_result in code_results]

            if all(code == 0 for code in exit_codes):
                summary = "\nAll code blocks executed successfully.\n"
                is_success = True
                # summary = f"exitcode: {code_result.exit_code} ({exitcode2str})\nCode output: \n{code_result.output}\n"
                # return True, f"\nAll code blocks executed successfully.\n{summary}"
            else:
                failed_blocks = sum(1 for code in exit_codes if code != 0)
                summary = f"\nExecution failed for {failed_blocks} code block(s).\n"
                # return True, f"\nExecution failed for {failed_blocks} code block(s).\n{summary}"

            for code_result in code_results:
                exitcode2str = (
                    "execution succeeded"
                    if code_result.exit_code == 0
                    else "execution failed"
                )
                summary += f"exitcode: {code_result.exit_code} ({exitcode2str})\nCode output: \n{code_result.output}\n"
                summary += "\n" + "-" * 50 + "\n"
            # print(summary)

        return is_success, summary
