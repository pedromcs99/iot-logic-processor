from celery import Celery
import redis
import pika
import json
import logging
import requests

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = "rabbitmq"
REDIS_HOST = "redis"
API_HOST = "http://api:8001"

# Configure Redis and Celery
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

celery_app = Celery(
    "app.tasks",
    broker=f"pyamqp://guest@{RABBITMQ_HOST}//",
    backend="rpc://"
)

OUTPUT_QUEUE = "machine_status"

def fetch_machine_logic(machine_id):
    """ Fetch custom logic from API or cache in Redis. """
    cache_key = f"machine_logic:{machine_id}"
    
    # Check Redis cache first
    logic = redis_client.get(cache_key)
    if logic:
        logger.info(f"✅ Using cached logic for {machine_id}")
        return logic

    # Fetch from API if not in cache
    try:
        response = requests.get(f"{API_HOST}/machines/{machine_id}/logic")
        response.raise_for_status()
        logic = response.json().get("logic")

        if logic:
            # Cache logic in Redis with 5-minute TTL
            redis_client.setex(cache_key, 300, logic)
            logger.info(f"🔄 Fetched and cached logic for {machine_id}")
            return logic
        else:
            logger.warning(f"⚠ No logic found for {machine_id}, using default.")
            return "def process(data, state): state['status'] = 'unknown'; return state"

    except requests.RequestException as e:
        logger.error(f"❌ Failed to fetch logic for {machine_id}: {e}")
        return "def process(data, state): state['status'] = 'error'; return state"

def execute_logic(logic_code, data, state):
    """ Dynamically execute the machine logic script. """
    try:
        local_scope = {}
        exec(logic_code, {}, local_scope)
        process_func = local_scope["process"]
        return process_func(data, state)
    except Exception as e:
        logger.error(f"❌ Error executing logic: {e}")
        return {"status": "error"}

def publish_result(machine_id, result):
    """ Publish the result back to RabbitMQ """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=OUTPUT_QUEUE, durable=True)

    channel.basic_publish(exchange="", routing_key=OUTPUT_QUEUE, body=json.dumps(result))
    connection.close()
    logger.info(f"📤 Published result: {result}")

@celery_app.task(name="app.tasks.process_machine_data")
def process_machine_data(message):
    """ Celery task to process machine data with custom logic """
    try:
        data = json.loads(message)
        machine_id = data["machine_id"]
        new_timestamp = data["timestamp"]
        new_signal = data["signal"]

        logger.info(f"⚙ Processing task for machine {machine_id}: {data}")

        # Retrieve last stored state from Redis
        last_state = redis_client.get(f"machine_state:{machine_id}")
        if last_state:
            last_state = json.loads(last_state)
        else:
            last_state = {"timestamp": None, "signal": None}

        logger.info(f"🔄 Last state for {machine_id}: {last_state}")

        # Fetch and execute custom logic
        logic_code = fetch_machine_logic(machine_id)
        updated_state = execute_logic(logic_code, data, last_state)

        # If the signal remains the same, do not update the timestamp
        if last_state.get("signal") == new_signal:
            updated_state["timestamp"] = last_state["timestamp"]
        else:
            updated_state["timestamp"] = new_timestamp  # Update timestamp if signal changed

        # Store the raw signal in Redis, but only update timestamp when signal changes
        redis_client.set(f"machine_state:{machine_id}", json.dumps({"signal": new_signal, "timestamp": updated_state["timestamp"], "status": updated_state["status"]}))

        # Publish result back to RabbitMQ
        result = {"machine_id": machine_id, **updated_state}
        publish_result(machine_id, result)

    except Exception as e:
        logger.error(f"❌ Error processing task: {e}")
