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
