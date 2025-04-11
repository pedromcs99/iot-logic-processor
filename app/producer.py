import pika
import json
import time
import random

RABBITMQ_HOST = "rabbitmq"
INPUT_QUEUE = "machine_data"

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=INPUT_QUEUE, durable=True)

MACHINES = ["machine_A", "machine_B", "machine_C"]

def send_mock_data():
    """ Simulate machines sending data at random intervals """
    while True:
        machine_id = random.choice(MACHINES)
        timestamp = int(time.time())
        signal = random.choice([0, 1])

        message = {"machine_id": machine_id, "timestamp": timestamp, "signal": signal}
        channel.basic_publish(exchange="", routing_key=INPUT_QUEUE, body=json.dumps(message))

        print(f"Sent: {message}")
        time.sleep(random.randint(1, 1))

if __name__ == "__main__":
    send_mock_data()
