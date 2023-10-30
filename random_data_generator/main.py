from kafka import KafkaProducer
from datetime import datetime
import time
from json import dumps
import random


KAFKA_TOPIC_NAME = "random_numbers"
KAFKA_BOOTSTRAP_SERVERS = '127.0.0.1:9093'
RANDOM_NUMBER_RANGE = (1, 10000)
NUMBER_OF_MESSAGES = 10000


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    kafka_producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda x: dumps(x).encode('utf-8'))

    for i in range(NUMBER_OF_MESSAGES):
        try:
            message = {}
            message_timestamp = datetime.now()
            print("Printing message id: " + str(i))
            message["id"] = str(i+1)
            message["timestamp"] = message_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            random.seed(datetime.now().second)
            message['value'] = random.randint(*RANDOM_NUMBER_RANGE)

            print("Sending message to Kafka topic: " + KAFKA_TOPIC_NAME)
            print("Message to be sent: ", message)
            kafka_producer.send(KAFKA_TOPIC_NAME, message)
        except Exception as ex:
            print("Event Message Construction Failed. ")
            print(ex)

        time.sleep(1)

