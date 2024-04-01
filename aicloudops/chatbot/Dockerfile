# Use an official lightweight Python base image
FROM python:3.10-slim-bullseye

# Set environment variables in one layer to reduce layer count
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget figlet ruby-full && \
    gem install lolcat && \
    pip install --upgrade pip

# Install bat from .deb package
RUN apt-get update && \
    apt-get install -y bat && \
    ln -s /usr/bin/batcat /usr/local/bin/bat

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ttyd (ensure compatibility or adjust as needed)
RUN wget https://github.com/tsl0922/ttyd/releases/download/1.7.5/ttyd.x86_64 -O /usr/local/bin/ttyd && \
    chmod +x /usr/local/bin/ttyd

# Create a non-root user to start the app
ARG USER=autogen
RUN useradd -m -s /bin/bash ${USER}

# Copy the current directory contents into the container at /app/
COPY --chown=${USER}:${USER} . .

EXPOSE 7681

# Command to run the application
# CMD ["ttyd", "--writable", "python", "src/main.py"]
CMD ["ttyd", "--writable", "python", "src/main.py"]

