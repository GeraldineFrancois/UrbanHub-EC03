import json
import os

from application.ports.outbound.alerte_publisher import AlertePublisher
from domain.entities.resultat_analyse import ResultatAnalyseTrafic

try:
    from kafka import KafkaProducer
except Exception:  # pragma: no cover - fallback env local sans kafka-python
    KafkaProducer = None


class KafkaAlertePublisher(AlertePublisher):
    def __init__(self, bootstrap_servers: str | None = None, topic: str | None = None, api_key: str = None):
        self.topic = topic or os.getenv("KAFKA_ALERT_TOPIC", "analyse.trafic.alertes")
        self.api_key = api_key or os.getenv("MS_API_KEY")
        servers = bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        self.producer = None

        if KafkaProducer and servers:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
            except Exception:
                self.producer = None

    def publier(self, resultat: ResultatAnalyseTrafic) -> None:
        if not self.producer:
            return

        payload = {
            "event_id": resultat.indicateur.event_id,
            "zone_id": resultat.indicateur.zone_id,
            "etat_trafic": resultat.indicateur.etat_trafic.value,
            "score": resultat.score_congestion.score,
            "niveau": resultat.score_congestion.niveau.value,
            "description": resultat.description,
            "date_heure": resultat.indicateur.date_heure.isoformat(),
        }
        headers = []
        if self.api_key:
            headers.append(("x-api-key", self.api_key.encode("utf-8")))
        self.producer.send(self.topic, payload, headers=headers or None)
