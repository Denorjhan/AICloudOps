# Use the official Python image, based on Debian, as the base image
FROM python:3.10-slim

# Set ARG variables
ARG USER=code_executor
ARG V_ENV=boto3venv
ARG VOLUME=/local-git

# Install essential system packages required for your application
RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        build-essential \
        libffi-dev \
        && rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN useradd -m -s /bin/bash ${USER}
USER ${USER}
WORKDIR /home/${USER}

# Add AWS credentials
RUN mkdir -p /home/${USER}/.aws
COPY aws/credentials /home/${USER}/.aws

# Create a virtual environment and activate it
RUN python3 -m venv ${V_ENV}
ENV PATH="/home/${USER}/${V_ENV}/bin:${PATH}"

# Set the environment variable PYTHONPATH
ENV PYTHONPATH=${VOLUME}

# Upgrade pip, setuptools, and wheel within the virtual environment
RUN pip install --upgrade pip setuptools wheel

# Install Python packages using pip in the virtual environment
COPY requirements.txt .
RUN pip install -r requirements.txt
