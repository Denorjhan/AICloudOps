import pika
import json

class RabbitMQConsumer:
    def __init__(self, queue_name='my_queue', host='rabbitmq', port=5672):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def callback(self, ch, method, properties, body):
        msg = body.decode()
        t = json.loads(msg)
        print(f" [x] Received {msg}")
        print(t)
        print(ch)
        print(method)
        print(properties)
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        print("started consumeing")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def close_connection(self):
        self.connection.close()


q = RabbitMQConsumer()
q.start_consuming()