# Guide de Prise en Main — MS6 Validateur

---

## Table des matières

1. [Prérequis](#1-prérequis)
2. [Cloner le repo](#2-cloner-le-repo)
3. [Installer les dépendances](#3-installer-les-dépendances)
4. [Exécuter les tests](#4-exécuter-les-tests)
5. [Lancer l'application localement](#5-lancer-lapplication-localement)
6. [Tester les endpoints](#6-tester-les-endpoints)
7. [Modifier le code](#7-modifier-le-code)
8. [Valider la qualité](#8-valider-la-qualité)
9. [Construire l'image Docker](#9-construire-limage-docker)
10. [Pousser le code](#10-pousser-le-code)
11. [Troubleshooting](#11-troubleshooting)
12. [Liens utiles](#12-liens-utiles)

---

## 1. Prérequis

| Outil | Version minimale | Vérification |
|---|---|---|
| Git | 2.x | `git --version` |
| Python | 3.11 | `python --version` |
| Poetry | 1.8+ | `poetry --version` |
| Docker | 24+ | `docker --version` |
| Docker Compose | 2.x | `docker compose version` |

**Installer Poetry si absent :**
```bash
pip install poetry
```

---

## 2. Cloner le repo

```bash
git clone https://github.com/GeraldineFrancois/UrbanHub-EC03.git
cd UrbanHub-EC03
git checkout feature/ms6-validateur-ec03
cd ms6-validateur-capteur
```

Structure attendue :
```
ms6-validateur-capteur/
├── src/
│   ├── config.py
│   ├── validator.py
│   └── main.py
├── tests/
│   ├── test_validator.py
│   └── test_main.py
├── Dockerfile
├── pyproject.toml
└── poetry.lock
```

---

## 3. Installer les dépendances

```bash
poetry install
poetry shell
```

Vérifier l'installation :
```bash
poetry run python -c "import fastapi; print(fastapi.__version__)"
# 0.136.1
```

---

## 4. Exécuter les tests

```bash
poetry run pytest tests/ -v --cov=src --cov-report=html
```

Résultat attendu :
```
11 passed in X.XXs
Coverage: 93%
Rapport HTML : htmlcov/index.html
```

Pour un rapport terminal uniquement :
```bash
poetry run pytest tests/ -v --cov=src --cov-report=term
```

---

## 5. Lancer l'application localement

```bash
poetry run uvicorn src.main:app --reload --port 8000
```

Ouvrir dans le navigateur :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **Health** : http://localhost:8000/health

---

## 6. Tester les endpoints

### GET /health

```bash
curl http://localhost:8000/health
```

Réponse :
```json
{"status": "healthy", "service": "ms6-validateur"}
```

### POST /validate — Cas normal (CO2 500 ppm)

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"sensor": "co2", "value": 500.0}'
```

Réponse :
```json
{
  "valid": true,
  "level": "normal",
  "sensor": "co2",
  "value": 500.0,
  "threshold": 800.0,
  "timestamp": "2026-04-29T10:00:00Z"
}
```

### POST /validate — Cas critique (CO2 1500 ppm)

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"sensor": "co2", "value": 1500.0}'
```

Réponse :
```json
{
  "valid": false,
  "level": "critical",
  "sensor": "co2",
  "value": 1500.0,
  "threshold": 1000.0,
  "timestamp": "2026-04-29T10:00:00Z"
}
```

### POST /validate — Capteur inconnu

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"sensor": "xyz", "value": 42.0}'
```

Réponse :
```json
{
  "valid": false,
  "level": "unknown",
  "sensor": "xyz",
  "value": 42.0,
  "threshold": null,
  "timestamp": "2026-04-29T10:00:00Z",
  "message": "Capteur non répertorié"
}
```

---

## 7. Modifier le code

### Fichiers importants

| Fichier | Rôle |
|---|---|
| `src/config.py` | Seuils des capteurs (`SENSOR_THRESHOLDS`) |
| `src/validator.py` | Logique de validation (`SensorValidator`) |
| `src/main.py` | Endpoints FastAPI |
| `tests/test_validator.py` | Suite de tests unitaires |
| `tests/test_main.py` | Tests d'intégration API |

### Exemple : ajouter un nouveau capteur

**1. Ajouter le capteur dans `src/config.py` :**
```python
SENSOR_THRESHOLDS = {
    "co2": {"moderate": 800, "critical": 1000, "unit": "ppm"},
    "temperature": {"moderate": 35, "critical": 40, "unit": "°C"},
    "noise": {"moderate": 70, "critical": 85, "unit": "dB"},
    "pm25": {"moderate": 25, "critical": 50, "unit": "μm/m³"},
    "humidity": {"moderate": 60, "critical": 80, "unit": "%"},  # nouveau
}
```

**2. Ajouter les tests dans `tests/test_validator.py` :**
```python
def test_normal_humidity(validator):
    result = validator.validate("humidity", 40.0)
    assert result["valid"] is True
    assert result["level"] == "normal"
```

**3. Relancer les tests :**
```bash
poetry run pytest tests/ -v --cov=src --cov-report=term
```

---

## 8. Valider la qualité

```bash
# Linting PEP8
flake8 src/ tests/

# Coverage + rapport XML (pour SonarCloud)
poetry run pytest tests/ --cov=src --cov-report=xml

# Sécurité des dépendances
snyk test --file=poetry.lock --package-manager=poetry
```

Résultats attendus :
```
flake8  : 0 erreur
coverage: 93%
snyk    : 0 vulnérabilité
```

---

## 9. Construire l'image Docker

```bash
# Build
docker build -t ms6-validateur:latest .

# Run
docker run -d -p 8000:8000 --name ms6-test ms6-validateur:latest

# Vérifier
curl http://localhost:8000/health

# Nettoyer
docker stop ms6-test && docker rm ms6-test
```

---

## 10. Pousser le code

```bash
# Créer une branche
git checkout -b feature/ma-modification

# Stager les fichiers modifiés
git add src/ tests/

# Commiter (Conventional Commits)
git commit -m "feat(ms6): ajout capteur humidity"

# Pousser
git push origin feature/ma-modification
```

Ensuite, créer une **Pull Request** sur GitHub vers `develop`.  
Le pipeline CI/CD se déclenche automatiquement : `test → quality → build → deploy-staging`.

---

## 11. Troubleshooting

**`ModuleNotFoundError: No module named 'src'`**
```bash
# Réinstaller dans le bon venv
poetry install
poetry shell
```

**`Port 8000 already in use`**
```bash
poetry run uvicorn src.main:app --reload --port 8001
```

**`Tests échouent : coverage < 80%`**
```bash
# Identifier les lignes non couvertes
poetry run pytest tests/ --cov=src --cov-report=term-missing
# Ajouter des tests pour les lignes marquées "Miss"
```

**`poetry.lock out of date`**
```bash
poetry lock
poetry install
```

**`Docker build échoue : curl not found`**
```bash
# Vérifier que curl est dans le Dockerfile
# Le Dockerfile actuel utilise python:3.11-slim qui inclut curl
docker build --no-cache -t ms6-validateur:latest .
```

---

## 12. Liens utiles

| Ressource | URL |
|---|---|
| Dépôt GitHub | https://github.com/GeraldineFrancois/UrbanHub-EC03 |
| Swagger UI (local) | http://localhost:8000/docs |
| SonarCloud | https://sonarcloud.io/project/overview?id=GeraldineFrancois_UrbanHub-EC03 |
| Documentation FastAPI | https://fastapi.tiangolo.com |
| Documentation Poetry | https://python-poetry.org/docs/ |
| Documentation pytest | https://docs.pytest.org/ |
| Snyk | https://app.snyk.io |
