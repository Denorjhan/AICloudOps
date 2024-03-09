# AICloudOps Manifesto

AICloudOps is dedicated to simplifying AWS CRUD operations, to lower the barrier of entry of cloud computing. It aims to make cloud computing accessible and efficient for users at various levels of technical expertise, while ensuring adherence to best practices.

## Agents

- **ProxyAgent**: Acts as the user's interface, facilitating chat-based communication. It orchestrates the operation by directing user requests to relevant agents and manages follow up questions to the user.

- **AwsSdkAgent**: Responsible for programatically managing AWS services, by generating and saving Python scripts using boto3 to the local enivronment.

- **ExecutorAgent**: Validates and runs code given to it and has the ability to debug, edit code, and revalidate/rerun the code. sends the code to the AwsSdkAggent to edit the code.


All agents must never make information up. If they need additional information, ask the ProxyAgent for assistance. The ProxyAgent will either ask the user for the additional info or assign the task to a different agent.

## Communication

The agency uses a chat-based interface for user communication via the ProxyAgent. The ProxyAgent then orchistrates the tasks amongst the appropriate agents on the team.

