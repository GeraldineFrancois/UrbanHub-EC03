from abc import ABC, abstractmethod
from domain.entities.indicateur_trafic import IndicateurTrafic
from typing import List


class IndicateurRepository(ABC):
    """
    Port sortant: ce que le domaine veut faire (envoyer une alerte)
    """
    
    @abstractmethod
    def save(self, indicateur: IndicateurTrafic) -> None:
        pass
    
    @abstractmethod
    def search_by_zone(self, zone_id: str) -> List[IndicateurTrafic]:
        pass
    