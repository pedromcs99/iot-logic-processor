import pika
import json
import time
import random
import requests

RABBITMQ_HOST = "localhost"
API_HOST = "http://localhost:8001"
INPUT_QUEUE = "machine_data"

MACHINES = {
    "machine_A": "def process(data, state): state['status'] = 'running' if data['signal'] == 1 else 'stopped'; return state",
    "machine_B": "def process(data, state): state['status'] = 'running' if data['timestamp'] % 2 == 0 else 'stopped'; return state",
    "machine_C": "def process(data, state): state['last_signal_timestamp'] = data['timestamp']; state['status'] = 'stopped' if ('last_signal_timestamp' in state and (data['timestamp'] - state['last_signal_timestamp']) > 20) else 'running'; return state",
    "machine_D": "def process(data, state): state['status'] = 'running' if data['signal'] == 1 else 'stopped'; return state"
}

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=INPUT_QUEUE, durable=True)

def register_machines():
    """ Register mock machines in the API before sending messages """
    headers = {"Content-Type": "application/json"}
    
    for machine_id, logic in MACHINES.items():
        response = requests.post(
            f"{API_HOST}/machines/create",
            json={"machine_id": machine_id, "logic": logic},
            headers=headers
        )

        if response.status_code == 200:
            print(f"✅ Registered machine {machine_id}")
        elif response.status_code == 400:
            print(f"⚠️ Machine {machine_id} already exists.")
        else:
            print(f"❌ Failed to register {machine_id}: {response.text}")

def send_mock_data():
    """ Simulate machines sending data at random intervals """
    while True:
        machine_id = random.choice(list(MACHINES.keys()))
        timestamp = int(time.time())
        signal = random.choice([0, 1])  # Simulate ON/OFF state

        message = {"machine_id": machine_id, "timestamp": timestamp, "signal": signal}
        channel.basic_publish(exchange="", routing_key=INPUT_QUEUE, body=json.dumps(message))

        print(f"📡 Sent: {message}")
        time.sleep(random.randint(5, 15))  # Wait before sending the next message

if __name__ == "__main__":
    print("🚀 Registering machines in API...")
    register_machines()
    print("📡 Starting mock data generator...")
    send_mock_data()
