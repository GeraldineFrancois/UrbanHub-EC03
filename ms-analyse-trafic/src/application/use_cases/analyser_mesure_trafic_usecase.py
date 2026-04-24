from domain.entities.mesure_trafic import MesureTrafic
from domain.entities.resultat_analyse import ResultatAnalyseTrafic
from domain.services.analyse_trafic_service import AnalyseTraficService
from application.ports.outbound.alerte_publisher import AlertePublisher
from application.ports.outbound.indicateur_repository import IndicateurRepository
from application.ports.outbound.score_repository import ScoreRepository

class AnalyserMesureTraficUseCase:
    """
    Use Case: Orchestre l'analyse d'une mesure de trafic
    C'est ici qu'on appelle le service métier
    """
    
    def __init__(
        self,
        analyse_service: AnalyseTraficService,
        indicateur_repository: IndicateurRepository,
        score_repository: ScoreRepository,
        alerte_publisher: AlertePublisher,
    ):
        self.analyse_service = analyse_service
        self.indicateur_repository = indicateur_repository
        self.score_repository = score_repository
        self.alerte_publisher = alerte_publisher
        
    def execute(self, mesure: MesureTrafic) -> ResultatAnalyseTrafic:
        """
        Point d'entrée principal du microservice
        """
        resultat = self.analyse_service.analyser(mesure)
        self.indicateur_repository.save(resultat.indicateur)
        self.score_repository.save(resultat.score_congestion)
        if resultat.doit_alerter:
            self.alerte_publisher.publier(resultat)
        return resultat