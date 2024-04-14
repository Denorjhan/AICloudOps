# AICloudOps Setup Guide

This guide will walk you through setting up this microservice project using Docker Compose. Please ensure you have the prerequisites listed below before you begin.

## Prerequisites

- Docker
- AWS Access Key ID and AWS Secret Access Key
- OPENAI API key: 
  - For instructions on how to obtain an OPENAI API key, visit [How to get an OPENAI API key](https://www.maisieai.com/help/how-to-get-an-openai-api-key-for-chatgpt).

## Setup Instructions

### Step 1: Clone the Repository

First, clone the project repository to your local machine using Git.

```bash
git clone https://github.com/Denorjhan/AICloudOps.git
cd aicloudops
```

### Step 2: 
Rename the `.env.example` file to `.env` using the command below.

```bash
mv .env.example .env
```

### Step 3:
 Enter your AWS and OPENAI values into the `.env` file. (setting OPENAI_MODEL to gpt-3.5-turbo-0125 is a very cost-effective model and should keep costs under a few cents)

 When using docker compose to run the project, the `RUNNING_IN` value should be set to `docker`.
 
 The postgress and rabbitmq values can be left as is.

 ```bash
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-3.5-turbo-0125
   AWS_ACCESS_KEY_ID=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_DEFAULT_REGION=your_aws_default_region
   RUNNING_IN=docker
 ```
### Step 4:

Run the following command to start the project.

```bash
docker compose up -d
```
Once the project is running, the app will be available at http://localhost:8080. The web app is simply a terminal emulator for the chatbot service

## Usage

- Once the app is running on http://localhost:8080, you can ask the chatbot to perform AWS CRUD operations.
- The chatbot will generate a python file to perform your requested action.
- You can then execute the code by pressing `ENTER` or provide any suggested changes to be made to the code.
- Any failed executions will result in the chatbot self-correcting the code based on the error message.


## TODO:
- [ ] Complete k8s manifests (configmaps, resource limits, liveness probes, tls ingress, etc.)
- [ ] Setup Prometheous & Grafana monitoring
- [ ] Add Pytest for source code
- [ ] Github Actions CI/CD
- [ ] Docs (architecture, design desicions)

