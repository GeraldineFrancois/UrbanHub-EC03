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