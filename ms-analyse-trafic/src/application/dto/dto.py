from pydantic import BaseModel
from datetime import datetime
from domain.entities.indicateur_trafic import IndicateurTrafic
from domain.entities.mesure_trafic import StatutCapteur
from domain.entities.score_congestion import ScoreCongestion
from domain.entities.resultat_analyse import ResultatAnalyseTrafic

class MesureTraficDTO(BaseModel):
    event_id: str
    capteur_id: str
    zone_id: str
    nombre_vehicule: int
    vitesse_moyenne: float
    taux_occupation: float
    date_heure: datetime | None = None
    statut_capteur: StatutCapteur = StatutCapteur.OK


class IndicateurTraficDTO(BaseModel):
    event_id: str
    zone_id: str
    date_heure: datetime
    densite: float
    vitesse_moyenne: float
    taux_occupation: float
    etat_trafic: str

    @staticmethod
    def from_entity(entity: IndicateurTrafic) -> "IndicateurTraficDTO":
        return IndicateurTraficDTO(
            event_id=entity.event_id,
            zone_id=entity.zone_id,
            date_heure=entity.date_heure,
            densite=entity.densite,
            vitesse_moyenne=entity.vitesse_moyenne,
            taux_occupation=entity.taux_occupation,
            etat_trafic=entity.etat_trafic.value,
        )


class ScoreCongestionDTO(BaseModel):
    zone_id: str
    date_heure: datetime
    score: float
    niveau: str

    @staticmethod
    def from_entity(entity: ScoreCongestion) -> "ScoreCongestionDTO":
        return ScoreCongestionDTO(
            zone_id=entity.zone_id,
            date_heure=entity.date_heure,
            score=entity.score,
            niveau=entity.niveau.value,
        )


class ResultatAnalyseDTO(BaseModel):
    indicateur: IndicateurTraficDTO
    score_congestion: ScoreCongestionDTO
    doit_alerter: bool
    description: str

    @staticmethod
    def from_entity(entity: ResultatAnalyseTrafic) -> "ResultatAnalyseDTO":
        return ResultatAnalyseDTO(
            indicateur=IndicateurTraficDTO.from_entity(entity.indicateur),
            score_congestion=ScoreCongestionDTO.from_entity(entity.score_congestion),
            doit_alerter=entity.doit_alerter,
            description=entity.description,
        )