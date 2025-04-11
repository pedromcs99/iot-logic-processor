import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")  
REDIS_HOST = os.getenv("REDIS_HOST", "redis") 