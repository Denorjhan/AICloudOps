# Use a Python 3.10 Alpine image as the base for a smaller footprint
FROM python:3.10-alpine as builder

# Install build dependencies for Python packages in one layer
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev cargo \
    && python3 -m venv /venv \
    && source /venv/bin/activate

# Set virtual environment as default
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies in .whl format to avoid recompilation
# Ensure requirements.txt specifies boto3 and its dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# Start a new stage from scratch for the final image
FROM python:3.10-alpine

# Create a non-root user for better security
RUN adduser -D code_executor

# Copy the built wheels and virtual environment from the previous stage
COPY --from=builder /wheels /wheels
COPY --from=builder /venv /venv

# Change ownership of the wheels and virtual environment before switching to the non-root user
RUN chown -R code_executor:code_executor /wheels /venv

# Now switch to the non-root user
USER code_executor
WORKDIR /home/code_executor

# Install the Python dependencies from wheels to avoid recompilation
RUN pip install --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

# Since this is a sandbox for boto3, ensure the Dockerfile does not include unnecessary packages
# Consider adding a .dockerignore file to exclude unnecessary files from the build context