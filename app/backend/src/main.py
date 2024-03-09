from CustomAgency import CustomAgency2
from agency_swarm.agency.agency import Agency
from AwsSdkAgent import AwsSdkAgent
from ProxyAgent import ProxyAgent
from ExecutorAgent import ExecutorAgent
from dotenv import load_dotenv
import os

load_dotenv()

proxy_agent = ProxyAgent()
aws_sdk_agent = AwsSdkAgent()
executoragent = ExecutorAgent()

agency = CustomAgency2([proxy_agent, 
                [proxy_agent, aws_sdk_agent],
                [proxy_agent, executoragent],
                [executoragent, aws_sdk_agent]],
                shared_instructions='./agency_manifesto.md')

if __name__ == '__main__':
    agency.run_demo() # CLI demo
  #  agency.demo_gradio() # Browser demo