"""Configuration des seuils de validation pour les capteurs UrbanHub."""

SENSOR_THRESHOLDS: dict[str, dict[str, int | str]] = {
    "co2": {"moderate": 800, "critical": 1000, "unit": "ppm"},
    "temperature": {"moderate": 35, "critical": 40, "unit": "°C"},
    "noise": {"moderate": 70, "critical": 85, "unit": "dB"},
    "pm25": {"moderate": 25, "critical": 50, "unit": "μm/m³"},
}


def get_thresholds(sensor_name: str) -> dict | None:
    """Retourne les seuils de validation pour un capteur donné.

    Args:
        sensor_name: Identifiant du type de capteur (ex: "co2", "temperature").

    Returns:
        Dictionnaire contenant les clés "moderate", "critical" et "unit",
        ou None si le capteur est inconnu.
    """
    return SENSOR_THRESHOLDS.get(sensor_name)
