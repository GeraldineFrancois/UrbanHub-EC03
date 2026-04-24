from datetime import datetime

from application.use_cases.analyser_mesure_trafic_usecase import AnalyserMesureTraficUseCase
from domain.entities.mesure_trafic import MesureTrafic, StatutCapteur
from domain.services.analyse_trafic_service import AnalyseTraficService


class FakeIndicateurRepository:
    def __init__(self):
        self.saved = []

    def save(self, indicateur):
        self.saved.append(indicateur)

    def search_by_zone(self, zone_id):
        return []


class FakeScoreRepository:
    def __init__(self):
        self.saved = []

    def save(self, score):
        self.saved.append(score)


class FakeAlertePublisher:
    def __init__(self):
        self.messages = []

    def publier(self, resultat):
        self.messages.append(resultat)


def test_use_case_persiste_et_publie_si_alerte():
    indic_repo = FakeIndicateurRepository()
    score_repo = FakeScoreRepository()
    publisher = FakeAlertePublisher()

    use_case = AnalyserMesureTraficUseCase(
        analyse_service=AnalyseTraficService(),
        indicateur_repository=indic_repo,
        score_repository=score_repo,
        alerte_publisher=publisher,
    )

    mesure = MesureTrafic(
        event_id="evt-alert",
        capteur_id="capteur-z",
        date_heure=datetime(2026, 4, 23, 8, 0, 0),
        zone_id="zone-z",
        nombre_vehicule=300,
        vitesse_moyenne=8.0,
        taux_occupation=0.99,
        statut_capteur=StatutCapteur.OK,
    )

    resultat = use_case.execute(mesure)

    assert len(indic_repo.saved) == 1
    assert len(score_repo.saved) == 1
    assert len(publisher.messages) == 1
    assert resultat.doit_alerter is True
