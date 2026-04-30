"""Logique métier de validation des données capteurs UrbanHub."""

import datetime

from config import get_thresholds


class SensorValidator:
    """Valide les mesures des capteurs urbains selon des seuils configurés."""

    def __init__(self) -> None:
        """Initialise le validateur en chargeant les seuils."""
        self._thresholds = get_thresholds

    def validate(self, sensor: str, value: float) -> dict:
        """Valide la mesure d'un capteur et retourne un rapport de validation.

        Args:
            sensor: Identifiant du type de capteur (ex: "co2", "temperature").
            value: Valeur mesurée par le capteur.

        Returns:
            Dictionnaire de validation avec les clés : valid, level, sensor,
            value, threshold, timestamp (et message si capteur inconnu).
        """
        thresholds = self._thresholds(sensor)

        if thresholds is None:
            return self._unknown_sensor_result(sensor, value)

        level = self._classify_level(value, thresholds)
        threshold = self._applicable_threshold(level, thresholds)

        return {
            "valid": level != "critical",
            "level": level,
            "sensor": sensor,
            "value": value,
            "threshold": threshold,
            "timestamp": self._now_iso(),
        }

    # ── Méthodes privées ────────────────────────────────────────────────────

    def _classify_level(self, value: float, thresholds: dict) -> str:
        """Classe la valeur en niveau normal, moderate ou critical."""
        if value >= thresholds["critical"]:
            return "critical"
        if value >= thresholds["moderate"]:
            return "moderate"
        return "normal"

    def _applicable_threshold(self, level: str, thresholds: dict) -> float:
        """Retourne le seuil pertinent selon le niveau détecté."""
        if level == "critical":
            return float(thresholds["critical"])
        return float(thresholds["moderate"])

    def _unknown_sensor_result(self, sensor: str, value: float) -> dict:
        """Construit le résultat pour un capteur non répertorié."""
        return {
            "valid": False,
            "level": "unknown",
            "sensor": sensor,
            "value": value,
            "threshold": None,
            "timestamp": self._now_iso(),
            "message": "Capteur non répertorié",
        }

    @staticmethod
    def _now_iso() -> str:
        """Retourne l'heure UTC courante au format ISO 8601."""
        return (
            datetime.datetime.now(datetime.timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
