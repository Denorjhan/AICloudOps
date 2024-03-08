from agency_swarm.agency.agency import Agency
import inspect
import json
import os
import readline
import shutil
import uuid
from enum import Enum
from typing import List, TypedDict, Callable, Any, Dict, Literal

from pydantic import Field, field_validator, validator
from rich.console import Console

from agency_swarm.agents import Agent
from agency_swarm.threads import Thread
from agency_swarm.tools import BaseTool
from agency_swarm.user import User

class CustomAgency (Agency):

    def _create_send_message_tool(self, agent: Agent, recipient_agents: List[Agent]):
        """
        Creates a SendMessage tool to enable an agent to send messages to specified recipient agents.


        Parameters:
            agent (Agent): The agent who will be sending messages.
            recipient_agents (List[Agent]): A list of recipient agents who can receive messages.

        Returns:
            SendMessage: A SendMessage tool class that is dynamically created and configured for the given agent and its recipient agents. This tool allows the agent to send messages to the specified recipients, facilitating inter-agent communication within the agency.
        """
        
        recipient_names = [agent.name for agent in recipient_agents]
        recipients = Enum("recipient", {name: name for name in recipient_names})


        agent_descriptions = ""
        for recipient_agent in recipient_agents:
            if not recipient_agent.description:
                continue
            agent_descriptions += recipient_agent.name + ": "
            agent_descriptions += recipient_agent.description + "\n"

        outer_self = self

        class SendMessage(BaseTool):
            _recipient_agents = recipient_agents

            instructions: str = Field(...,
                                      description="Please repeat your instructions step-by-step, including both completed "
                                                  "and the following next steps that you need to perfrom. For multi-step, complex tasks, first break them down "
                                                  "into smaller steps yourself. Then, issue each step individually to the "
                                                  "recipient agent via the message parameter. Each identified step should be "
                                                  "sent in separate message. Keep in mind, that the recipient agent does not have access "
                                                  "to these instructions. You must include recipient agent-specific instructions "
                                                  "in the message parameter.")
            recipient: recipients = Field(..., description=agent_descriptions)
            message: str = Field(...,
                                 description="Specify the task required for the recipient agent to complete. Focus on "
                                             "clarifying what the task entails, rather than providing exact "
                                             "instructions.")
            """message_files: List[str] = Field(default=None,
                                             description="A list of file ids to be sent as attachments to this message. Only use this if you have the exact file name.",
                                             examples=["list_s3_buckets.py", "create_dev_enironment.py"])"""

         #   @validator('recipient')
            @validator('recipient')
            def check_recipient(cls, value):
                if value not in recipients:
                    raise ValueError(f"Recipient {value} is not valid.")
                return value

            @classmethod
            def schema(cls, by_alias: bool = True):
                original_schema = super().model_json_schema(by_alias=by_alias)
                #recipient_enum = cls.model_fields['recipient'].type_

                # Create the $defs section with the recipient enum
                defs = {
                    "recipient": {
                        "enum": [e.value for e in recipients],
                        "title": "recipient",
                        "type": "string"
                    }
                }

                # Update the original schema to include $defs and a $ref for the recipient field
                original_schema.update({
                    "$defs": defs
                })
                original_schema['properties']['recipient'] = {
                    "allOf": [
                        {"$ref": "#/$defs/recipient"}
                    ],
                    "description": original_schema['properties']['recipient']['description']  # Keep the existing description
                }

                return original_schema

            class Config:
                arbitrary_types_allowed = True



            @validator('message', pre=True)
            def check_message(cls, v):
                if not v.strip():  # This checks if the message is not just whitespace
                    raise ValueError("The message field must not be empty.")
                return v
            
            @validator('instructions', pre=True)
            def check_instructions(cls, v):
                if not v.strip():  # This checks if the instructions is not just whitespace
                    raise ValueError("The instructions field must not be empty.")
                return v

            def run(self):
                thread = outer_self.agents_and_threads[self.caller_agent.name][self.recipient.value]

                if not outer_self.async_mode:
                    gen = thread.get_completion(message=self.message)#, message_files=self.message_files)
                    try:
                        while True:
                            yield next(gen)
                    except StopIteration as e:
                        message = e.value
                else:
                    message = thread.get_completion_async(message=self.message)#, message_files=self.message_files)

                return message or ""

        SendMessage.caller_agent = agent
        if self.async_mode:
            SendMessage.__doc__ = self.send_message_tool_description_async
        else:
            SendMessage.__doc__ = self.send_message_tool_description

        return SendMessage


class CustomAgency2(Agency):

    def _create_send_message_tool(self, agent: Agent, recipient_agents: List[Agent]):
        """
        Creates a SendMessage tool to enable an agent to send messages to specified recipient agents.


        Parameters:
            agent (Agent): The agent who will be sending messages.
            recipient_agents (List[Agent]): A list of recipient agents who can receive messages.

        Returns:
            SendMessage: A SendMessage tool class that is dynamically created and configured for the given agent and its recipient agents. This tool allows the agent to send messages to the specified recipients, facilitating inter-agent communication within the agency.
        """
        recipient_names = [agent.name for agent in recipient_agents]
        recipients = Enum("recipient", {name: name for name in recipient_names})

        agent_descriptions = ""
        for recipient_agent in recipient_agents:
            if not recipient_agent.description:
                continue
            agent_descriptions += recipient_agent.name + ": "
            agent_descriptions += recipient_agent.description + "\n"

        outer_self = self

        class SendMessage(BaseTool):
            instructions: str = Field(...,
                                      description="Please repeat your instructions step-by-step, including both completed "
                                                  "and the following next steps that you need to perfrom. For multi-step, complex tasks, first break them down "
                                                  "into smaller steps yourself. Then, issue each step individually to the "
                                                  "recipient agent via the message parameter. Each identified step should be "
                                                  "sent in separate message. Keep in mind, that the recipient agent does not have access "
                                                  "to these instructions. You must include recipient agent-specific instructions "
                                                  "in the message parameter.")
            recipient: recipients = Field(..., description=agent_descriptions)
            message: str = Field(...,
                                 description="Specify the task required for the recipient agent to complete. Focus on "
                                             "clarifying what the task entails, rather than providing exact "
                                             "instructions.")
            """files: List[str] = Field(default=None,
                                             description="A list of exact file names to be sent as attachments to this message. Only use this if you have the exact file name.",
                                             examples=["ec2.py", "list_s3.py"])"""

            @field_validator('recipient')
            def check_recipient(cls, value):
                if value.value not in recipient_names:
                    raise ValueError(f"Recipient {value} is not valid. Valid recipients are: {recipient_names}")
                return value

            def run(self):
                thread = outer_self.agents_and_threads[self.caller_agent.name][self.recipient.value]

                if not outer_self.async_mode:
                    gen = thread.get_completion(message=self.message)#, message_files=self.message_files)
                    try:
                        while True:
                            yield next(gen)
                    except StopIteration as e:
                        message = e.value
                else:
                    message = thread.get_completion_async(message=self.message)#, message_files=self.message_files)

                return message or ""

        SendMessage.caller_agent = agent
        if self.async_mode:
            SendMessage.__doc__ = self.send_message_tool_description_async
        else:
            SendMessage.__doc__ = self.send_message_tool_description

        return SendMessage
