import pika
import json

class RabbitMQPublisher:
    def __init__(self, host='rabbitmq', queue_name='my_queue'):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def publish(self, message: dict):
        """
        Publishes a message to the queue.

        :param message: The message to be published. Must be a dictionary.
        """
        
        message = json.dumps(message)  # Convert to JSON string

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent, 
            )
        )
        print(f" [x] Sent '{message}' to queue '{self.queue_name}'")

    def log_execution(self, file_path: str, exit_code: int, output: str):
        # create a single dict from the params
        log = {
            'file_path': file_path,
            'exit_code': exit_code,
            'output': output
        }
        self.publish(log)
    
    def close_connection(self):
        if self.connection.is_open:
            self.connection.close()
            
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()





# code_file, last_exit_code, code_output = "/example/path", 0, "sample output"

# with QueuePublisher() as queue:
#     queue.log_execution(code_file, last_exit_code, code_output)