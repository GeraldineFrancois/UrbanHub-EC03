import os
import threading

from fastapi import FastAPI
from adapters.inbound.controller import router
from adapters.inbound.kafka_collecte_consumer import KafkaCollecteConsumer
from adapters.inbound.controller import build_use_case
from infrastructure.database.database.database import init_db
from infrastructure.database.database.database import SessionLocal

app = FastAPI(
    title="ms-analyse-trafic",
    version="1.0.0",
)

app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    init_db()
    if os.getenv("KAFKA_CONSUMER_ENABLED", "false").lower() != "true":
        return

    def handle_mesure(mesure):
        db = SessionLocal()
        try:
            use_case = build_use_case(db)
            use_case.execute(mesure)
        finally:
            db.close()

    consumer = KafkaCollecteConsumer(message_handler=handle_mesure)
    if consumer.consumer:
        thread = threading.Thread(target=consumer.consommer, daemon=True)
        thread.start()

@app.get("/health")
def health():
    return {"status": "ok"}