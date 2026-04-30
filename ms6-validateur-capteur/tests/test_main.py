"""Tests d'intégration pour l'API FastAPI MS6."""

import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from main import app  # noqa: E402

client = TestClient(app)


def test_validate_missing_field():
    """Vérifie que l'API retourne 422 si le payload est incomplet."""
    response = client.post("/validate", json={"sensor": "co2"})
    assert response.status_code == 422
