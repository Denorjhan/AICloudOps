import pika
import os


class CodeExecutionPublisher:
    def __init__(
        self,
        queue_name="code_execution",
        host=None,
        port=None,
        username=None,
        password=None,
    ):
        self.queue_name = queue_name
        self.host = host or os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.port = int(port or os.getenv("RABBITMQ_PORT", 5672))
        self.username = username or os.getenv("RABBITMQ_USERNAME")
        self.password = password or os.getenv("RABBITMQ_PASSWORD")
        self.connection = None
        self.channel = None

        try:
            self.ensure_connection()
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")

    def ensure_connection(self):
        """Ensures that the connection to RabbitMQ is open, reconnects if necessary."""
        if self.connection is None or not self.connection.is_open:
            self.open_connection()
        if self.channel is None or not self.channel.is_open:
            self.open_channel()

    def open_connection(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host, port=self.port, credentials=credentials
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def publish(self, message: str):
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
        )

    def close_connection(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

    # for garbage collection
    def __del__(self):
        self.close_connection()
