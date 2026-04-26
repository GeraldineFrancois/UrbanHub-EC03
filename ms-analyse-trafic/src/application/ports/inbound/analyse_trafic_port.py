from abc import ABC, abstractmethod
from domain.entities.mesure_trafic import MesureTrafic
from domain.entities.resultat_analyse import ResultatAnalyseTrafic

class TraficEventHandlerPort(ABC):
    """
    Port entrant : ce que le monde extérieur peut demander au domaine.
    contrat que l'adapter (FastAPI ou Kafka consumer)
    utilise pour déclencher l'analyse.
    Le domaine implémente ce port via AnalyseTraficService.
    """
    
    @abstractmethod
    def analyser(self, mesure: MesureTrafic) -> ResultatAnalyseTrafic:
        pass
    