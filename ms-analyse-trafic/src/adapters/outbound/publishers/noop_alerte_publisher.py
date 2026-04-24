from application.ports.outbound.alerte_publisher import AlertePublisher
from domain.entities.resultat_analyse import ResultatAnalyseTrafic


class NoopAlertePublisher(AlertePublisher):
    def publier(self, resultat: ResultatAnalyseTrafic) -> None:
        return None
