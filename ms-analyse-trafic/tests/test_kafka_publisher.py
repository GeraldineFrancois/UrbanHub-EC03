from datetime import datetime

from adapters.outbound.publishers.kafka_alerte_publisher import KafkaAlertePublisher
from domain.entities.indicateur_trafic import EtatTrafic, IndicateurTrafic
from domain.entities.resultat_analyse import ResultatAnalyseTrafic
from domain.entities.score_congestion import NiveauCongestion, ScoreCongestion


class FakeProducer:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.sent = []

    def send(self, topic, payload, headers=None):
        self.sent.append({"topic": topic, "payload": payload, "headers": headers})


def _resultat() -> ResultatAnalyseTrafic:
    indicateur = IndicateurTrafic(
        event_id="evt-1",
        zone_id="zone-a",
        date_heure=datetime(2026, 4, 23, 8, 0, 0),
        densite=1.2,
        vitesse_moyenne=18.5,
        taux_occupation=0.8,
        etat_trafic=EtatTrafic.CONGESTED,
    )
    score = ScoreCongestion(
        zone_id="zone-a",
        date_heure=datetime(2026, 4, 23, 8, 0, 0),
        score=7.4,
        niveau=NiveauCongestion.HIGH,
    )
    return ResultatAnalyseTrafic(
        indicateur=indicateur,
        score_congestion=score,
        doit_alerter=True,
        description="alerte",
    )


def test_kafka_publisher_envoie_message_avec_api_key(monkeypatch):
    monkeypatch.setattr(
        "adapters.outbound.publishers.kafka_alerte_publisher.KafkaProducer",
        FakeProducer,
    )

    publisher = KafkaAlertePublisher(
        bootstrap_servers="localhost:9092",
        topic="analyse.trafic.alertes",
        api_key="secret-key",
    )
    publisher.publier(_resultat())

    sent = publisher.producer.sent
    assert len(sent) == 1
    assert sent[0]["topic"] == "analyse.trafic.alertes"
    assert sent[0]["payload"]["zone_id"] == "zone-a"
    assert ("x-api-key", b"secret-key") in sent[0]["headers"]


def test_kafka_publisher_ignore_si_non_connecte(monkeypatch):
    monkeypatch.setattr(
        "adapters.outbound.publishers.kafka_alerte_publisher.KafkaProducer",
        None,
    )
    publisher = KafkaAlertePublisher(bootstrap_servers="localhost:9092")
    publisher.publier(_resultat())
    assert publisher.producer is None
