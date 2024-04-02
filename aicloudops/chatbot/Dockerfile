FROM python:3.10-slim-bullseye

# prevent .pyc files for smaller size container size and prevent buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# Install system dependencies in a single RUN command to reduce layers.
# Install ttyd from source, compatible versions with this image are not available from package managers
# Clean up after to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget figlet ruby-full bat && \
    ln -s /usr/bin/batcat /usr/local/bin/bat && \
    gem install lolcat && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    wget https://github.com/tsl0922/ttyd/releases/download/1.7.5/ttyd.x86_64 -O /usr/local/bin/ttyd && \
    chmod +x /usr/local/bin/ttyd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user to start the app
ARG USER=autogen
RUN useradd -m -s /bin/bash ${USER}
COPY --chown=${USER}:${USER} . .
USER ${USER}

EXPOSE 7681

# Command to run the application
CMD ["ttyd", "--writable", "python", "src/main.py"]