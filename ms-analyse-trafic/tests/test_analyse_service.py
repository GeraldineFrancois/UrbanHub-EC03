from datetime import datetime

from domain.entities.mesure_trafic import MesureTrafic, StatutCapteur
from domain.entities.score_congestion import NiveauCongestion
from domain.services.analyse_trafic_service import AnalyseTraficService


def _mesure(vitesse: float, occupation: float, date_heure: datetime) -> MesureTrafic:
    return MesureTrafic(
        event_id="evt-test",
        capteur_id="capteur-x",
        date_heure=date_heure,
        zone_id="zone-x",
        nombre_vehicule=100,
        vitesse_moyenne=vitesse,
        taux_occupation=occupation,
        statut_capteur=StatutCapteur.OK,
    )


def test_analyse_service_retourne_low_en_circulation_fluide():
    service = AnalyseTraficService()
    resultat = service.analyser(_mesure(vitesse=55.0, occupation=0.20, date_heure=datetime(2026, 4, 25, 11, 0, 0)))
    assert resultat.doit_alerter is False
    assert resultat.score_congestion.niveau == NiveauCongestion.LOW


def test_analyse_service_retourne_critical_en_forte_congestion():
    service = AnalyseTraficService()
    resultat = service.analyser(_mesure(vitesse=9.0, occupation=0.98, date_heure=datetime(2026, 4, 23, 8, 0, 0)))
    assert resultat.doit_alerter is True
    assert resultat.score_congestion.niveau == NiveauCongestion.CRITICAL
