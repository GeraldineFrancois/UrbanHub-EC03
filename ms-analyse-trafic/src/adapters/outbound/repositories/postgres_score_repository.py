from adapters.outbound.models.score_congestion_model import ScoreCongestionModel
from application.ports.outbound.score_repository import ScoreRepository
from domain.entities.score_congestion import ScoreCongestion


class PostgresScoreRepository(ScoreRepository):
    def __init__(self, db):
        self.db = db

    def save(self, score: ScoreCongestion) -> None:
        model = ScoreCongestionModel(
            zone_id=score.zone_id,
            date_heure=score.date_heure,
            score=score.score,
            niveau=score.niveau.value,
        )
        self.db.add(model)
        self.db.commit()
