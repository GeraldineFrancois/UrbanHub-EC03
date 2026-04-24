pour un microservice analyseTrafic, j'ai deja etabli le domaine avec la logique metier, voici aussie les ports, maintenant je passe au prochaine etape de l'architecture hexagonale, que faire maintenant? pour la base de données j'utilise postgresql,  que faire d'abord? et explique toujours ce que tu fais et pourquoi. je veux tester avec swagger mon backend. je te donne aussi les tables de mon database, dit moi si c'est coherent ou pas.

from datetime import datetime
from enum import Enum
from dataclasses import dataclass


class EtatTrafic(str, Enum):
    """enum for EtatTrafic."""

    FREE = "FREE"
    MODERATE = "MODERATE"
    DENSE = "DENSE"
    CONGESTED = "CONGESTED"
    CRITICAL = "CRITICAL"


@dataclass
class IndicateurTrafic:
    event_id: str
    zone_id: str
    date_heure: datetime
    densite: float
    vitesse_moyenne: float
    taux_occupation: float
    etat_trafic: EtatTrafic


from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class StatutCapteur(str, Enum):
    OK = "OK"
    OFFLINE = "OFFLINE"
    BROKEN = "BROKEN"


@dataclass
class MesureTrafic:
    event_id: str
    capteur_id: str
    date_heure: datetime
    zone_id: str
    nombre_vehicule: int
    vitesse_moyenne: float
    taux_occupation: float
    statut_capteur: StatutCapteur

from dataclasses import dataclass
from domain.entities.indicateur_trafic import IndicateurTrafic
from domain.entities.score_congestion import ScoreCongestion


@dataclass
class ResultatAnalyseTrafic:
    indicateur: IndicateurTrafic
    score_congestion: ScoreCongestion
    doit_alerter: bool
    description: str

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class NiveauCongestion(str, Enum):
    LOW = ("LOW")
    MEDIUM = ("MEDIUM")
    HIGH = ("HIGH")
    CRITICAL = ("CRITICAL")


@dataclass
class ScoreCongestion:
    zone_id: str
    date_heure: datetime
    score: float  # entre 0 et 10
    niveau: NiveauCongestion

from entities.score_congestion import ScoreCongestion
from entities.indicateur_trafic import IndicateurTrafic
from entities.indicateur_trafic import EtatTrafic
from entities.mesure_trafic import MesureTrafic
from entities.resultat_analyse import ResultatAnalyseTrafic
from entities.score_congestion import NiveauCongestion
from datetime import datetime


class AnalyseTraficService(AnalyseTraficPort):

    VITESSE_NORMALE_KMH = 45.0

    def _get_vitesse_normale(self, date_heure: datetime) -> float:
        heure = date_heure.hour

        # Heure de pointe matin et soir (lundi-vendredi)
        if date_heure.weekday() < 5:  # 0=lundi ... 4=vendredi
            if 7 <= heure <= 9 or 16 <= heure <= 18:
                return 28.0  # vitesse moyenne acceptable en pointe
            else:
                return 45.0  # vitesse normale hors pointe
        else:
            return 45.0  # weekend

    def analyser(self, mesure: MesureTrafic) -> ResultatAnalyseTrafic:
        """
        service pour analyser le trafic

        """
        vitesse_normale = self._get_vitesse_normale(mesure.date_heure)

        # 1. Calcul réduction de vitesse par rapport à la normale du moment
        if mesure.vitesse_moyenne >= vitesse_normale:
            reduction = 0.0
        else:
            reduction = (vitesse_normale - mesure.vitesse_moyenne) / vitesse_normale

        # 2. Calcul score congestion
        score = (reduction * 0.60) + (mesure.taux_occupation * 0.40)
        score = round(min(max(score * 10, 0.0), 10.0), 2)

        # 3. Détermination état et niveau
        etat, niveau = self._determiner_etat_niveau(
            mesure.vitesse_moyenne, mesure.taux_occupation, score, vitesse_normale
        )
        
        indicateur = IndicateurTrafic(
            event_id=mesure.event_id,
            zone_id=mesure.zone_id,
            date_heure=mesure.date_heure,
            densite=round(mesure.nombre_vehicule / 100.0, 2),
            vitesse_moyenne=mesure.vitesse_moyenne,
            taux_occupation=mesure.taux_occupation,
            etat_trafic=etat
        )
        
        score_congestion = ScoreCongestion(
            zone_id=mesure.zone_id,
            date_heure=mesure.date_heure,
            score=score,
            niveau=niveau
        )

        doit_alerter = niveau in [NiveauCongestion.HIGH, NiveauCongestion.CRITICAL]

        description = (
            f"{etat.upper()} - {mesure.vitesse_moyenne:.1f} km/h "
            f"(normal {vitesse_normale:.0f}) - Occupation {mesure.taux_occupation*100:.0f}%"
        )

        return ResultatAnalyseTrafic(
            indicateur=indicateur,
            score_congestion=score_congestion,
            doit_alerter=doit_alerter,
            description=description
        )

    def _determiner_etat_niveau(
        self, vitesse: float, occupation: float, score: float, vitesse_normale: float
    ):
        if score >= 8.5 or vitesse < 12:
            return EtatTrafic.CRITICAL, NiveauCongestion.CRITICAL
        elif score >= 6.5 or vitesse < 20:
            return EtatTrafic.CONGESTED, NiveauCongestion.HIGH
        elif score >= 4.0 or vitesse < 30:
            return EtatTrafic.DENSE, NiveauCongestion.MEDIUM
        elif vitesse < vitesse_normale - 5:
            return EtatTrafic.MODERATE, NiveauCongestion.MEDIUM
        else:
            return EtatTrafic.FREE, NiveauCongestion.LOW


import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

from fastapi import FastAPI

app = FastAPI(
    title="ms-analyse-trafic",
    version="0.1.0",
)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}

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


from abc import ABC, abstractmethod
from domain.entities.resultat_analyse import ResultatAnalyseTrafic
from domain.entities.indicateur_trafic import IndicateurTrafic


class IndicateurRepository(ABC):
    """
    Port sortant: ce que le domaine veut faire (envoyer une alerte)
    """
    @abstractmethod
    def publier_alerte(self, alerte: dict) -> bool:
        """
        Retourne True si l'alerte a bien été publiée
        """
        pass
    
    @abstractmethod
    def save(self, indicateur: IndicateurTrafic) -> None:
        pass
    
    @abstractmethod
    def search_by_zone(self, zone_id:str) -> List[IndicateurTrafic]:
        pass
    
from domain.entities.mesure_trafic import MesureTrafic
from domain.entities.resultat_analyse import ResultatAnalyseTrafic
from domain.services.analyse_trafic_service import AnalyseTraficService

class AnalyserMesureTraficUseCase:
    """
    Use Case: Orchestre l'analyse d'une mesure de trafic
    C'est ici qu'on appelle le service métier
    """
    
    def __init__(self, analyse_service: AnalyseTraficService):
        self.analyse_service = analyse_service
        
    def execute(self, mesure: MesureTrafic) -> ResultatAnalyseTrafic:
        """
        Point d'entrée principal du microservice
        """
        return self.analyse_service.analyser(mesure)


voici le controller.py (adapters/inbound/controller.py):
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from domain.entities.mesure_trafic import MesureTrafic
from application.use_cases.analyser_mesure_trafic_usecase import AnalyserMesureTraficUseCase
from domain.services.analyse_trafic_service import AnalyseTraficService

router = APIRouter()

class MesureRequest(BaseModel):
    event_id:str
    capteur_id:str
    zone_id: str
    nombre_vehicule: int
    vitesse_moyenne:float
    taux_occupation:float
    
@router.post("/analyse")
def analyser_mesure(request: MesureRequest):
    mesure = MesureTrafic(
        event_id=request.event_id,
        capteur_id=request.capteur_id,
        zone_id=request.zone_id,
        nombre_vehicule=request.nombre_vehicule,
        vitesse_moyenne=request.vitesse_moyenne,
        taux_occupation=request.taux_occupation,
        date_heure=datetime.utcnow(),
        statut_capteur="OK"
    )
    
    use_case = AnalyserMesureTraficUseCase(AnalyseTraficService())
    resultat = use_case.execute(mesure)
    
    return resultat

voici dans adapters/outbound/models/indicateur_model.py :
from sqlalchemy import Column, String, Float, DateTime
from infrastructure.database import database


class IndicateurModel(Base):
    __tablename__ = "indicateur_trafic"
    event_id = Column(String, primary_key=True)
    zone_id = Column(String)
    date_heure = Column(DateTime)
    densite = Column(Float)
    vitesse_moyenne = Column(Float)
    taux_occupation = Column(Float)
    etat_trafic = Column(String)

voici le Dockerfile: 

FROM python:3.13-slim

WORKDIR /app

ENV POETRY_REQUESTS_TIMEOUT=600 \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction

COPY . .

EXPOSE 8003

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]

voici le Docker-compose.yml :

services:
  ms-analyse-service:
    build: .
    container_name: ms_analyse_trafic
    ports:
      - "8003:8003"
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:postgres@postgres:5432/analyse_trafic_db
      JWT_SECRET_KEY: "change-me-in-production"
      JWT_ALGORITHM: "HS256"
      JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "30"

  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: root
      POSTGRES_DB: analyse_trafic_db
    ports:
      - "5432:5432"
    volumes:
      - ./src/infrastructure//database/database/db_analyse_trafic.sql:/docker-entrypoint-initdb.d/00_db_analyse_trafic.sql:ro
