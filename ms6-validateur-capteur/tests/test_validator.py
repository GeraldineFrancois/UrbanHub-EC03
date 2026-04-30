"""Tests unitaires pour SensorValidator."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from validator import SensorValidator  # noqa: E402


@pytest.fixture
def validator():
    """Instance partagée de SensorValidator."""
    return SensorValidator()


# ── CO2 ─────────────────────────────────────────────────────────────────────

def test_normal_co2(validator):
    result = validator.validate("co2", 500.0)
    assert result["valid"] is True
    assert result["level"] == "normal"
    assert result["sensor"] == "co2"
    assert result["value"] == 500.0
    assert result["threshold"] == 800.0
    assert "timestamp" in result


def test_critical_co2(validator):
    result = validator.validate("co2", 1500.0)
    assert result["valid"] is False
    assert result["level"] == "critical"
    assert result["sensor"] == "co2"
    assert result["value"] == 1500.0
    assert result["threshold"] == 1000.0
    assert "timestamp" in result


# ── Température ─────────────────────────────────────────────────────────────

def test_normal_temperature(validator):
    result = validator.validate("temperature", 30.0)
    assert result["valid"] is True
    assert result["level"] == "normal"
    assert result["sensor"] == "temperature"
    assert result["value"] == 30.0
    assert result["threshold"] == 35.0
    assert "timestamp" in result


def test_critical_temperature(validator):
    result = validator.validate("temperature", 42.0)
    assert result["valid"] is False
    assert result["level"] == "critical"
    assert result["sensor"] == "temperature"
    assert result["value"] == 42.0
    assert result["threshold"] == 40.0
    assert "timestamp" in result


# ── Bruit ────────────────────────────────────────────────────────────────────

def test_normal_noise(validator):
    result = validator.validate("noise", 60.0)
    assert result["valid"] is True
    assert result["level"] == "normal"
    assert result["sensor"] == "noise"
    assert result["value"] == 60.0
    assert result["threshold"] == 70.0
    assert "timestamp" in result


def test_critical_noise(validator):
    result = validator.validate("noise", 90.0)
    assert result["valid"] is False
    assert result["level"] == "critical"
    assert result["sensor"] == "noise"
    assert result["value"] == 90.0
    assert result["threshold"] == 85.0
    assert "timestamp" in result


# ── PM2.5 ────────────────────────────────────────────────────────────────────

def test_normal_pm25(validator):
    result = validator.validate("pm25", 20.0)
    assert result["valid"] is True
    assert result["level"] == "normal"
    assert result["sensor"] == "pm25"
    assert result["value"] == 20.0
    assert result["threshold"] == 25.0
    assert "timestamp" in result


def test_critical_pm25(validator):
    result = validator.validate("pm25", 60.0)
    assert result["valid"] is False
    assert result["level"] == "critical"
    assert result["sensor"] == "pm25"
    assert result["value"] == 60.0
    assert result["threshold"] == 50.0
    assert "timestamp" in result


# ── Capteurs inconnus ────────────────────────────────────────────────────────

def test_unknown_sensor(validator):
    result = validator.validate("unknown", 100.0)
    assert result["valid"] is False
    assert result["level"] == "unknown"
    assert result["sensor"] == "unknown"
    assert result["value"] == 100.0
    assert result["threshold"] is None
    assert "timestamp" in result
    assert result["message"] == "Capteur non répertorié"


def test_invalid_sensor_type(validator):
    result = validator.validate("xyz", 42.0)
    assert result["valid"] is False
    assert result["level"] == "unknown"
    assert result["sensor"] == "xyz"
    assert result["value"] == 42.0
    assert result["threshold"] is None
    assert "timestamp" in result
    assert result["message"] == "Capteur non répertorié"
