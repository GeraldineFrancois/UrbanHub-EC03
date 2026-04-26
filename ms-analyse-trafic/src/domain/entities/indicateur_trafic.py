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
