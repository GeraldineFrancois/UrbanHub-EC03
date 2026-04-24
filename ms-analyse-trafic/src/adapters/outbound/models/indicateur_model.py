from sqlalchemy import Column, String, Float, DateTime
from infrastructure.database.database.database import Base


class IndicateurModel(Base):
    __tablename__ = "indicateur_trafic"
    event_id = Column(String, primary_key=True, index=True)
    zone_id = Column(String, nullable=False, index=True)
    date_heure = Column(DateTime, nullable=False, index=True)
    densite = Column(Float, nullable=False)
    vitesse_moyenne = Column(Float, nullable=False)
    taux_occupation = Column(Float, nullable=False)
    etat_trafic = Column(String, nullable=False)
