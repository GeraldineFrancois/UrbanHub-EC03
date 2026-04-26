from typing import List

from adapters.outbound.models.indicateur_model import IndicateurModel
from application.ports.outbound.indicateur_repository import IndicateurRepository
from domain.entities.indicateur_trafic import EtatTrafic, IndicateurTrafic


class PostgresIndicateurRepository(IndicateurRepository):
    def __init__(self, db):
        self.db = db

    def save(self, indicateur: IndicateurTrafic) -> None:
        model = IndicateurModel(
            event_id=indicateur.event_id,
            zone_id=indicateur.zone_id,
            date_heure=indicateur.date_heure,
            densite=indicateur.densite,
            vitesse_moyenne=indicateur.vitesse_moyenne,
            taux_occupation=indicateur.taux_occupation,
            etat_trafic=indicateur.etat_trafic.value,
        )
        self.db.add(model)
        self.db.commit()

    def search_by_zone(self, zone_id: str) -> List[IndicateurTrafic]:
        rows = self.db.query(IndicateurModel).filter(IndicateurModel.zone_id == zone_id).all()
        return [
            IndicateurTrafic(
                event_id=row.event_id,
                zone_id=row.zone_id,
                date_heure=row.date_heure,
                densite=row.densite,
                vitesse_moyenne=row.vitesse_moyenne,
                taux_occupation=row.taux_occupation,
                etat_trafic=EtatTrafic(row.etat_trafic),
            )
            for row in rows
        ]
