from datetime import datetime

from application.ports.inbound.analyse_trafic_port import TraficEventHandlerPort
from domain.entities.indicateur_trafic import EtatTrafic, IndicateurTrafic
from domain.entities.mesure_trafic import MesureTrafic
from domain.entities.resultat_analyse import ResultatAnalyseTrafic
from domain.entities.score_congestion import NiveauCongestion, ScoreCongestion


class AnalyseTraficService(TraficEventHandlerPort):

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
        CAPACITE_MAX = 200
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
            densite= min(mesure.nombre_vehicule / CAPACITE_MAX, 1.0),
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
