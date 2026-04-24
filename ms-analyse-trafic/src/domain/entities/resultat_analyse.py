from dataclasses import dataclass
from domain.entities.indicateur_trafic import IndicateurTrafic
from domain.entities.score_congestion import ScoreCongestion


@dataclass
class ResultatAnalyseTrafic:
    indicateur: IndicateurTrafic
    score_congestion: ScoreCongestion
    doit_alerter: bool
    description: str
