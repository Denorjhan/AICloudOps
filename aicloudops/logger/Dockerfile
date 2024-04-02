# Stage 1: Build environment
FROM python:3.10-slim-buster as builder

# prevent .pyc files for smaller size container size and prevent buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# Install system dependencies in a single RUN command to reduce layers
# Clean up after to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* 

# Create a non-root user and set the appropriate permissions to start the app
ARG USER=logger
RUN useradd -m -s /bin/bash ${USER}
COPY --chown=${USER}:${USER} . .
USER ${USER}

RUN if [ -f wait_for_rabbitmq.sh ]; then chmod +x wait_for_rabbitmq.sh; fi

# The ENTRYPOINT remains the same
ENTRYPOINT ["./wait_for_rabbitmq.sh"]

# The CMD remains the same
CMD ["python", "src/main.py"]
