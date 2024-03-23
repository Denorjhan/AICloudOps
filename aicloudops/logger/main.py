from orm.database import init_db
from messaging.consumer import RabbitMQConsumer



def main():
    print("in main function!!!!")
    #listen for msgs, processes hash, insert in db
    
    
    with RabbitMQConsumer() as q: 
        q.start_consuming() 
        


if __name__ == "__main__":
    try:
        init_db()
        print("sdfas")
        main() 
    except Exception as e:
        print(f"An error occurred: {e}")