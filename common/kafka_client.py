import json
import logging
import os
from typing import Any, Dict, Optional

from kafka import KafkaConsumer, KafkaProducer

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092",
)
TODO_TOPIC = os.getenv("KAFKA_TODO_TOPIC", "todos-created")

_producer: Optional[KafkaProducer] = None


def get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        logger.info("Creating Kafka producer for %s", KAFKA_BOOTSTRAP_SERVERS)
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda v: json.dumps(v).encode("utf-8") if v is not None else None,
        )
    return _producer


def send_todo_created_event(todo_id: int, title: str) -> None:
    producer = get_producer()
    payload: Dict[str, Any] = {
        "todo_id": todo_id,
        "title": title,
    }
    producer.send(TODO_TOPIC, value=payload, key={"todo_id": todo_id})


def create_todo_consumer(group_id: str = "todo-generator") -> KafkaConsumer:
    return KafkaConsumer(
        TODO_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id,
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        key_deserializer=lambda v: json.loads(v.decode("utf-8")) if v is not None else None,
        auto_offset_reset="earliest",
    )
