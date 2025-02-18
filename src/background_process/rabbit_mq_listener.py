import json
import os

import pika
from dotenv import load_dotenv

from src.config import KNOWLEDGE_DB
from src.controllers import add_knowledge_func
from src.utils.news import get_news

load_dotenv()

time_clear_cache = int(os.getenv('TIME_CLEAR_CACHE', 3000))
RABBITMQ_HOST, RABBITMQ_PORT = os.getenv('ENV_EVENTBUS_CONNECTION', 'localhost:5672').split(':')
RABBITMQ_RETRY = int(os.getenv('ENV_EVENTBUS_RETRY', '2'))
RABBITMQ_USERNAME = os.getenv('ENV_EVENTBUS_USERNAME', 'guest')
RABBITMQ_PASSWORD = os.getenv('ENV_EVENTBUS_PASSWORD', 'guest')
QUEUE_NAME = os.getenv('ENV_EVENTBUS_SUBSCRIPTION_CLIENTNAME', 'dev-queue-tripgo-service_local')
ROUTING_KEYS = [
    'NewsModifyEventIntegration',
]


# RabbitMQ callback function
def callback(ch, method, properties, body):
    print(f" [x] Received method: {method}, properties: {properties}, ch: {ch}")
    body = body.decode('utf-8')
    body = json.loads(body)
    status = body.get('Status', 'error')
    news_id = body.get('NewsId', None)
    if status == 'DELETED' and news_id:
        KNOWLEDGE_DB.delete({'docGuid': news_id})
        return
    data = get_news(news_id)
    if data is None:
        return
    subject = data.get('title', '')
    content = data.get('content', '')
    add_knowledge_func(subject, content, 'gemini', doc_guid=news_id)


# Biến toàn cục để lưu trữ kết nối
rabbitmq_connection = None
rabbitmq_channel = None


# RabbitMQ setup function
def setup_rabbitmq():
    global rabbitmq_connection, rabbitmq_channel

    if rabbitmq_connection is not None and rabbitmq_connection.is_open:
        return

    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=int(RABBITMQ_PORT),
        credentials=credentials,
        connection_attempts=RABBITMQ_RETRY
    )

    try:
        rabbitmq_connection = pika.BlockingConnection(parameters)
        rabbitmq_channel = rabbitmq_connection.channel()
        rabbitmq_channel.queue_delete(queue=QUEUE_NAME)
        rabbitmq_channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True,
        )
        for routing_key in ROUTING_KEYS:
            rabbitmq_channel.queue_bind(
                queue=QUEUE_NAME,
                exchange='eshop_event_bus',
                routing_key=routing_key
            )
        rabbitmq_channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=True
        )
        print(f' [*] Connected to RabbitMQ, waiting for messages on queue {QUEUE_NAME}.')
    except Exception as exc:
        print(f"Failed to connect to RabbitMQ: {exc}")
        rabbitmq_connection = None
        rabbitmq_channel = None


# RabbitMQ process messages function
def process_rabbitmq_messages():
    global rabbitmq_connection, rabbitmq_channel
    if rabbitmq_channel is not None and rabbitmq_channel.is_open:
        rabbitmq_connection.process_data_events(time_limit=2)  # Non-blocking, process for 1 second
    else:
        setup_rabbitmq()
