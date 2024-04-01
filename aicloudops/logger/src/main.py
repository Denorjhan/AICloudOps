from orm.database import init_db
from modules.consumer import RabbitMQConsumer
from time import sleep

def main():
    with RabbitMQConsumer() as q: 
        q.start_consuming() 
    # while True:
    #     print("In loop")
    #     sleep(20)
        

if __name__ == "__main__":
    try:
        init_db()
        main() 
    except Exception as e:
        print(f"An error occurred: {e}")