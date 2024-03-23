import pika
import json

class RabbitMQConsumer:
    def __init__(self, host='rabbitmq', queue_name='my_queue'):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def callback(self, ch, method, properties, body):
        msg = body.decode()
        t = json.loads(msg)
        print(f" [x] Received {msg}")
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        print("started consuming")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def close_connection(self):
        if self.connection.is_open:
            self.connection.close()
            
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()




# with RabbitMQConsumer() as q: 
#     q.start_consuming()