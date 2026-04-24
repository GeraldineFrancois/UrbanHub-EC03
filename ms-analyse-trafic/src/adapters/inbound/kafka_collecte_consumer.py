import json
import os
from datetime import datetime

from kafka import KafkaConsumer

from application.ports.inbound.collecte_consumer import CollecteConsumer
from domain.entities.mesure_trafic import MesureTrafic, StatutCapteur


class KafkaCollecteConsumer(CollecteConsumer):
    def __init__(
        self,
        message_handler,
        bootstrap_servers: str | None = None,
        topic: str | None = None,
        api_key: str | None = None,
        group_id: str = "analyse-trafic-consumer-group",
    ):
        self.topic = topic or os.getenv("KAFKA_COLLECTE_TOPIC", "collecte.iot")
        self.expected_api_key = api_key or os.getenv("MS_API_KEY")
        self.message_handler = message_handler
        servers = bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        self.consumer = None

        if servers:
            try:
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=servers,
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                    auto_offset_reset="latest",
                    enable_auto_commit=True,
                    group_id=group_id,
                )
            except Exception:
                self.consumer = None

    @staticmethod
    def _headers_to_dict(headers) -> dict:
        if not headers:
            return {}
        result = {}
        for key, value in headers:
            if isinstance(value, bytes):
                result[key] = value.decode("utf-8")
            else:
                result[key] = value
        return result

    def _is_api_key_valid(self, payload: dict, headers: dict) -> bool:
        if not self.expected_api_key:
            return True
        provided = headers.get("x-api-key") or payload.get("api_key")
        return provided == self.expected_api_key

    def _to_mesure(self, data: dict) -> MesureTrafic:
        date_heure = data.get("date_heure")
        if isinstance(date_heure, str):
            date_heure = datetime.fromisoformat(date_heure)
        if not date_heure:
            date_heure = datetime.utcnow()

        statut = data.get("statut_capteur", StatutCapteur.OK)
        if isinstance(statut, str):
            statut = StatutCapteur(statut)

        return MesureTrafic(
            event_id=data["event_id"],
            capteur_id=data["capteur_id"],
            date_heure=date_heure,
            zone_id=data["zone_id"],
            nombre_vehicule=data["nombre_vehicule"],
            vitesse_moyenne=data["vitesse_moyenne"],
            taux_occupation=data["taux_occupation"],
            statut_capteur=statut,
        )

    def consommer_message(self, message) -> None:
        payload = message.value or {}
        headers = self._headers_to_dict(getattr(message, "headers", None))
        if not self._is_api_key_valid(payload, headers):
            return
        mesure = self._to_mesure(payload)
        self.message_handler(mesure)

    def consommer(self) -> None:
        if not self.consumer:
            return
        for message in self.consumer:
            try:
                self.consommer_message(message)
            except Exception:
                continue