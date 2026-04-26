from sqlalchemy import Column, DateTime, Float, Integer, String

from infrastructure.database.database.database import Base


class ScoreCongestionModel(Base):
    __tablename__ = "score_congestion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(String, nullable=False, index=True)
    date_heure = Column(DateTime, nullable=False, index=True)
    score = Column(Float, nullable=False)
    niveau = Column(String, nullable=False)
