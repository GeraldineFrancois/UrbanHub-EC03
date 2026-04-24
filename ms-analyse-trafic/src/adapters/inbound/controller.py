from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from adapters.outbound.publishers.kafka_alerte_publisher import KafkaAlertePublisher
from adapters.outbound.publishers.noop_alerte_publisher import NoopAlertePublisher
from adapters.outbound.repositories.postgres_indicateur_repository import (
    PostgresIndicateurRepository,
)
from adapters.outbound.repositories.postgres_score_repository import PostgresScoreRepository
from application.dto.dto import MesureTraficDTO, ResultatAnalyseDTO
from domain.entities.mesure_trafic import MesureTrafic
from domain.services.analyse_trafic_service import AnalyseTraficService
from application.use_cases.analyser_mesure_trafic_usecase import AnalyserMesureTraficUseCase
from infrastructure.database.database.database import get_db


router = APIRouter()


def build_use_case(db: Session) -> AnalyserMesureTraficUseCase:
    publisher = KafkaAlertePublisher()
    if not publisher.producer:
        publisher = NoopAlertePublisher()

    return AnalyserMesureTraficUseCase(
        analyse_service=AnalyseTraficService(),
        indicateur_repository=PostgresIndicateurRepository(db),
        score_repository=PostgresScoreRepository(db),
        alerte_publisher=publisher,
    )


def get_use_case(db: Session = Depends(get_db)) -> AnalyserMesureTraficUseCase:
    return build_use_case(db)


@router.post("/analyse", response_model=ResultatAnalyseDTO)
def analyser_mesure(
    request: MesureTraficDTO,
    use_case: AnalyserMesureTraficUseCase = Depends(get_use_case),
):
    mesure = MesureTrafic(
        event_id=request.event_id,
        capteur_id=request.capteur_id,
        zone_id=request.zone_id,
        nombre_vehicule=request.nombre_vehicule,
        vitesse_moyenne=request.vitesse_moyenne,
        taux_occupation=request.taux_occupation,
        date_heure=request.date_heure or datetime.utcnow(),
        statut_capteur=request.statut_capteur,
    )

    resultat = use_case.execute(mesure)
    return ResultatAnalyseDTO.from_entity(resultat)
