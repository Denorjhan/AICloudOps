# Dockerfile
FROM python:3.8

WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your application code and the entry point script
COPY . /app


CMD ["python", "main.py"]  
