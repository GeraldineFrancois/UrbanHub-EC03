from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from main import app
from adapters.inbound.controller import get_use_case
from domain.entities.indicateur_trafic import EtatTrafic, IndicateurTrafic
from domain.entities.resultat_analyse import ResultatAnalyseTrafic
from domain.entities.score_congestion import NiveauCongestion, ScoreCongestion


class FakeUseCase:
    def execute(self, mesure):
        score = 9.1 if mesure.vitesse_moyenne <= 10 else 3.2
        niveau = NiveauCongestion.CRITICAL if score >= 8.5 else NiveauCongestion.LOW
        etat = EtatTrafic.CRITICAL if niveau == NiveauCongestion.CRITICAL else EtatTrafic.FREE
        return ResultatAnalyseTrafic(
            indicateur=IndicateurTrafic(
                event_id=mesure.event_id,
                zone_id=mesure.zone_id,
                date_heure=mesure.date_heure,
                densite=round(mesure.nombre_vehicule / 100.0, 2),
                vitesse_moyenne=mesure.vitesse_moyenne,
                taux_occupation=mesure.taux_occupation,
                etat_trafic=etat,
            ),
            score_congestion=ScoreCongestion(
                zone_id=mesure.zone_id,
                date_heure=mesure.date_heure,
                score=score,
                niveau=niveau,
            ),
            doit_alerter=niveau in [NiveauCongestion.HIGH, NiveauCongestion.CRITICAL],
            description="resultat mock",
        )


def _override_use_case():
    return FakeUseCase()


def test_analyse_endpoint_retourne_resultat():
    payload = {
        "event_id": f"evt-{uuid4()}",
        "capteur_id": "capteur-1",
        "zone_id": "zone-a",
        "nombre_vehicule": 120,
        "vitesse_moyenne": 35.0,
        "taux_occupation": 0.42,
        "date_heure": datetime(2026, 4, 23, 10, 30, 0).isoformat(),
        "statut_capteur": "OK",
    }

    app.dependency_overrides[get_use_case] = _override_use_case
    with TestClient(app) as client:
        response = client.post("/analyse", json=payload)
    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["indicateur"]["event_id"] == payload["event_id"]
    assert data["score_congestion"]["zone_id"] == payload["zone_id"]
    assert isinstance(data["doit_alerter"], bool)


def test_analyse_endpoint_declenche_alerte_si_critique():
    payload = {
        "event_id": f"evt-{uuid4()}",
        "capteur_id": "capteur-2",
        "zone_id": "zone-b",
        "nombre_vehicule": 250,
        "vitesse_moyenne": 8.0,
        "taux_occupation": 0.95,
        "date_heure": datetime(2026, 4, 23, 8, 15, 0).isoformat(),
        "statut_capteur": "OK",
    }

    app.dependency_overrides[get_use_case] = _override_use_case
    with TestClient(app) as client:
        response = client.post("/analyse", json=payload)
    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["doit_alerter"] is True
    assert data["score_congestion"]["niveau"] in ["HIGH", "CRITICAL"]
