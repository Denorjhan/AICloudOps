# Dockerfile
FROM python:3.8

WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN apt-get update && \
    apt-get install -y netcat-openbsd && \
    rm -rf /var/lib/apt/lists/* 

# RUN apt-get update
# RUN apt-get install -y netcat-openbsd
# RUN rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your application code and the entry point script
COPY . /app
RUN chmod +x wait_for_rabbitmq.sh

ENTRYPOINT [ "./wait_for_rabbitmq.sh" ] 
CMD ["python", "main.py"]  

