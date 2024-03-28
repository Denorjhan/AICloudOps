# Use an official lightweight Python base image
FROM python:3.10-slim-buster

# Set environment variables in one layer to reduce layer count
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


# Set working directory
WORKDIR /app

# Combine the upgrade of pip and installation of dependencies into a single RUN to reduce layers
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget figlet && \
    apt-get install -y ruby-full && \
    gem install lolcat && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN wget https://github.com/tsl0922/ttyd/releases/download/1.7.5/ttyd.x86_64 -O /usr/local/bin/ttyd && \
    chmod +x /usr/local/bin/ttyd

# Create a non-root user to start the app, avoiding setting up unnecessary directories as root
ARG USER=autogen
RUN useradd -m -s /bin/bash ${USER} 
# RUN useradd -m -s /bin/bash ${USER} && \
#     mkdir -p /Volumes/aicode && \ 
#     chown -R ${USER}:${USER} /Volumes/aicode  

# RUN useradd -m -s /bin/bash ${USER} && \
#     mkdir -p aicode && \
#     chown -R ${USER}:${USER} .

# Use the non-root user
#USER ${USER}

# Copy the current directory contents into the container at /app/
# This is done after setting the user to avoid having to chown later
COPY --chown=${USER}:${USER} . . 

EXPOSE 7681

# Command to run the application
CMD ["ttyd", "--writable", "-p", "8080", "python", "src/main.py"]
# CMD ["ttyd", "-p", "7681", "bash"]

