
#! NOTE: the WORKDIR is set during runtime when the app creates the container.
FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

COPY requirements.txt .

# Activate the virtual environment and install the dependencies. 
# Since the requirments.txt will not be changed frequently even in the dev environment, we can do this in one RUN command to minimize layers & image size.
RUN python3 -m venv /venv \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create a non-root user and set the appropriate permissions to start the app
ARG USER=code_executor
RUN useradd -m -s /bin/bash ${USER} \
    && chown -R ${USER}:${USER} /venv
USER ${USER}
