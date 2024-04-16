from orm.database import init_db
from modules.consumer import RabbitMQConsumer


def main():
    with RabbitMQConsumer() as q:
        q.start_consuming()


if __name__ == "__main__":
    try:
        init_db()
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
