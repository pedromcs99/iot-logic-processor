import pika
import json
import logging
from tasks import process_machine_data

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = "rabbitmq"
INPUT_QUEUE = "machine_data"

def connect_to_rabbitmq():
    """ Retry connection to RabbitMQ until it's available. """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    return connection

# Establish RabbitMQ connection
connection = connect_to_rabbitmq()
channel = connection.channel()
channel.queue_declare(queue=INPUT_QUEUE, durable=True)

def enqueue_task(ch, method, properties, body):
    """ Receive a message from RabbitMQ and send it to Celery """
    data = json.loads(body)
    machine_id = data["machine_id"]

    logger.info(f"📥 Received message for {machine_id}: {data}")

    try:
        # Send task to Celery (make sure it goes to the correct queue)
        process_machine_data.apply_async(args=[json.dumps(data)], queue="celery")
        logger.info(f"🚀 Task sent to Celery for {machine_id}")
    except Exception as e:
        logger.error(f"❌ Failed to send task to Celery: {e}")

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    logger.info(f"✅ Message acknowledged for {machine_id}")

channel.basic_consume(queue=INPUT_QUEUE, on_message_callback=enqueue_task)
logger.info("🎧 Waiting for messages...")
channel.start_consuming()
