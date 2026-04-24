from abc import ABC, abstractmethod
from domain.entities.resultat_analyse import ResultatAnalyseTrafic
from domain.entities.indicateur_trafic import IndicateurTrafic


class AlertePublisher(ABC):
    """
    Port sortant: ce que le domaine veut faire (envoyer une alerte)
    """
    @abstractmethod
    def publier(self, resultat: ResultatAnalyseTrafic) -> None:
        pass