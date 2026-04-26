from adapters.inbound.kafka_collecte_consumer import KafkaCollecteConsumer
from domain.entities.mesure_trafic import StatutCapteur


class FakeMessage:
    def __init__(self, value, headers=None):
        self.value = value
        self.headers = headers or []


class FakeKafkaConsumer:
    def __init__(self, *args, **kwargs):
        self._messages = []

    def __iter__(self):
        return iter(self._messages)


def test_consumer_traite_message_si_api_key_valide(monkeypatch):
    traite = []
    monkeypatch.setattr("adapters.inbound.kafka_collecte_consumer.KafkaConsumer", FakeKafkaConsumer)

    consumer = KafkaCollecteConsumer(
        message_handler=lambda m: traite.append(m),
        bootstrap_servers="localhost:9092",
        api_key="expected",
    )
    msg = FakeMessage(
        value={
            "event_id": "evt-1",
            "capteur_id": "cap-1",
            "zone_id": "zone-a",
            "nombre_vehicule": 44,
            "vitesse_moyenne": 30.0,
            "taux_occupation": 0.5,
            "statut_capteur": "OK",
        },
        headers=[("x-api-key", b"expected")],
    )

    consumer.consommer_message(msg)
    assert len(traite) == 1
    assert traite[0].zone_id == "zone-a"
    assert traite[0].statut_capteur == StatutCapteur.OK


def test_consumer_ignore_message_si_api_key_invalide(monkeypatch):
    traite = []
    monkeypatch.setattr("adapters.inbound.kafka_collecte_consumer.KafkaConsumer", FakeKafkaConsumer)

    consumer = KafkaCollecteConsumer(
        message_handler=lambda m: traite.append(m),
        bootstrap_servers="localhost:9092",
        api_key="expected",
    )
    msg = FakeMessage(
        value={
            "event_id": "evt-2",
            "capteur_id": "cap-2",
            "zone_id": "zone-b",
            "nombre_vehicule": 11,
            "vitesse_moyenne": 55.0,
            "taux_occupation": 0.2,
            "statut_capteur": "OK",
        },
        headers=[("x-api-key", b"wrong-key")],
    )

    consumer.consommer_message(msg)
    assert traite == []