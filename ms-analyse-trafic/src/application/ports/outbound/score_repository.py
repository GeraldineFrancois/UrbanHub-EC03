from abc import ABC, abstractmethod

from domain.entities.score_congestion import ScoreCongestion


class ScoreRepository(ABC):
    @abstractmethod
    def save(self, score: ScoreCongestion) -> None:
        pass
