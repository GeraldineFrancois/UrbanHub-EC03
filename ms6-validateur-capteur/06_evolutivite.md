# Évolutivité & Intégration — MS6 Validateur de Données Capteur

---

## Table des matières

1. [Positionnement dans UrbanHub](#1-positionnement-dans-urbanhub)
2. [Intégration avec les autres microservices](#2-intégration-avec-les-autres-microservices)
3. [Évolutions futures possibles](#3-évolutions-futures-possibles)
4. [Performance & Scalabilité](#4-performance--scalabilité)
5. [Sécurité](#5-sécurité)
6. [Maintenance](#6-maintenance)
7. [Risques & Mitigations](#7-risques--mitigations)
8. [Roadmap](#8-roadmap)

---

## 1. Positionnement dans UrbanHub

```
Capteurs IoT (CO2, Température, Bruit, PM2.5)
         |
         | données brutes
         v
+------------------------+
|   MS Collecte IoT      |  reçoit et transmet les mesures
+------------------------+
         |
         | POST /validate
         v
+------------------------+
|  [MS6 VALIDATEUR]      |  ← TU ES ICI
|  classify: normal /    |
|  moderate / critical   |
+------------------------+
         |
         | JSON classifié
         v
+------------------------+
|  MS Analyse Trafic     |  consomme les données validées
+------------------------+
         |
         v
+------------------------+
|  MS Alerte             |  déclenche alertes si critical
+------------------------+
         |
         v
   Stockage + Dashboard
```

**Rôle de MS6 :** Garantir que seules des données qualifiées (niveau connu, seuil évalué) progressent dans le système. Sans cette étape, MS Analyse Trafic traiterait des données brutes sans contexte de criticité.

---

## 2. Intégration avec les autres microservices

### Contrat d'interface

| Attribut | Valeur |
|---|---|
| Protocol | HTTP REST |
| Format | JSON |
| Endpoint entrant | `POST /validate` |
| Endpoint monitoring | `GET /health` |
| Port | 8000 |

### Flux d'une mesure capteur

**1. MS Collecte envoie :**
```json
{"sensor": "co2", "value": 850.0}
```

**2. MS6 répond :**
```json
{
  "valid": true,
  "level": "moderate",
  "sensor": "co2",
  "value": 850.0,
  "threshold": 800.0,
  "timestamp": "2026-04-29T10:00:00Z"
}
```

**3. MS Analyse Trafic consomme la classification** et applique sa logique métier uniquement sur `level` et `valid` — sans recalculer les seuils.

### Découplage

MS6 ne connaît pas ses consommateurs. Il expose une interface REST standard. Tout microservice peut l'interroger sans modification de MS6.

---

## 3. Évolutions futures possibles

### A. Ajouter de nouveaux capteurs

**Effort : faible — 2 fichiers à modifier**

```python
# src/config.py — ajouter l'entrée
SENSOR_THRESHOLDS = {
    ...
    "humidity":            {"moderate": 60,  "critical": 80,  "unit": "%"},
    "co":                  {"moderate": 9,   "critical": 35,  "unit": "ppm"},
    "particulate_matter_10": {"moderate": 50, "critical": 100, "unit": "μg/m³"},
}
```

```python
# tests/test_validator.py — ajouter le test
def test_normal_humidity(validator):
    result = validator.validate("humidity", 40.0)
    assert result["valid"] is True
    assert result["level"] == "normal"
```

La logique `SensorValidator` ne change pas — elle est générique par conception.

---

### B. Seuils dynamiques (depuis une base de données)

**Effort : moyen — refactoriser `config.py`**

Actuellement, les seuils sont codés en dur dans un dictionnaire. Pour les rendre configurables à chaud :

```python
# Futur config.py
def get_thresholds(sensor_name: str) -> dict | None:
    """Charge les seuils depuis un service de configuration externe."""
    response = requests.get(f"http://config-service/thresholds/{sensor_name}")
    return response.json() if response.ok else None
```

Impact : ajouter un cache (Redis) pour éviter une requête HTTP à chaque validation.

---

### C. Prédiction ML

**Effort : élevé — nouvelle dépendance, nouveau service**

```
Actuellement : valeur → seuil → classification binaire
Futur        : historique de valeurs → modèle LSTM → probabilité de dépassement futur
```

```python
# Futur validator.py
from sklearn.preprocessing import MinMaxScaler
import joblib

model = joblib.load("models/co2_predictor.pkl")

def predict_future_level(sensor: str, history: list[float]) -> str:
    ...
```

Impact : ajouter `scikit-learn`, `joblib`, pipeline de réentraînement.

---

### D. Intégration Kafka / Event Bus

**Effort : moyen — parallèle à l'architecture existante**

Le microservice `ms-analyse-trafic` utilise déjà Kafka. MS6 peut adopter le même pattern :

```
Actuellement : HTTP sync (MS Collecte → POST /validate → réponse immédiate)
Futur        : Kafka async (MS Collecte publie → MS6 consomme → publie résultat)
```

```python
# Futur kafka_consumer.py (pattern identique à ms-analyse-trafic)
class KafkaValidateurConsumer:
    def consommer(self):
        for message in self.consumer:
            result = self.validator.validate(
                message["sensor"], message["value"]
            )
            self.producer.send("validated-readings", result)
```

FastAPI resterait disponible en parallèle pour les appels synchrones.

---

### E. Monitoring avancé

**Effort : faible — ajout de dépendances**

```python
# Futur main.py — métriques Prometheus
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

validations_total = Counter("ms6_validations_total", "Total validations", ["level"])
Instrumentator().instrument(app).expose(app)
```

| Évolution | Dépendance | Impact |
|---|---|---|
| Métriques Prometheus | `prometheus-fastapi-instrumentator` | faible |
| Logs structurés | `structlog` | faible |
| Tracing distribué | `opentelemetry-sdk` | moyen |

---

## 4. Performance & Scalabilité

### État actuel

| Métrique | Valeur estimée |
|---|---|
| Capacité | ~1 000 req/sec (uvicorn, instance unique) |
| Latence | < 10ms par validation (calcul pur, sans I/O) |
| CPU | Minimal — validation en mémoire uniquement |
| Mémoire | < 100 MB (FastAPI + dépendances) |

### Pour scaler horizontalement

```
                    ┌─────────────────┐
                    │  Load Balancer  │  nginx / Traefik
                    └────────┬────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
      ┌────────────┐  ┌────────────┐  ┌────────────┐
      │  MS6 :8000 │  │  MS6 :8001 │  │  MS6 :8002 │
      └────────────┘  └────────────┘  └────────────┘
```

- **Kubernetes** : HorizontalPodAutoscaler sur CPU/RPS
- **Redis** : cache des thresholds si chargement externe
- **Async/await** : nécessaire uniquement si I/O externe (DB, Kafka)

---

## 5. Sécurité

### État actuel

| Indicateur | Valeur |
|---|---|
| Vulnérabilités Snyk | 0 |
| Dépendances à jour | Oui (`requests 2.33`, `urllib3 2.6.3`, `idna 3.13`) |
| Coverage | 93% |
| Authentification | Aucune (service interne uniquement) |

### Améliorations futures

| Amélioration | Priorité | Impact |
|---|---|---|
| Authentification OAuth2 / JWT | Haute | Protège l'endpoint si exposé publiquement |
| Rate limiting par IP/source | Moyenne | Prévient les abus et le DoS |
| Audit logging | Moyenne | Traçabilité des validations critiques |
| Chiffrement TLS | Haute | Si MS6 traverse un réseau non sécurisé |
| Rotation automatique des secrets | Haute | Intégration Vault ou GitHub Secrets |

---

## 6. Maintenance

### Tâches récurrentes

| Fréquence | Tâche | Commande |
|---|---|---|
| Hebdomadaire | Audit sécurité | `snyk test --file=poetry.lock` |
| Mensuel | Mise à jour dépendances | `poetry update && poetry run pytest tests/` |
| Continue (CI) | Analyse qualité | SonarCloud sur chaque push |
| Par sprint | Revue couverture | `poetry run pytest --cov=src --cov-report=term-missing` |

### Métriques à maintenir

| Métrique | Seuil cible |
|---|---|
| Coverage | ≥ 80% |
| Vulnérabilités | 0 |
| Latence p99 | < 100ms |
| Disponibilité | ≥ 99.5% |
| Code Smells SonarCloud | 0 |

---

## 7. Risques & Mitigations

| # | Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Seuils incohérents entre environnements | Moyenne | Élevé | `config.py` centralisé, tests couvrant tous les seuils |
| 2 | Volume élevé (IoT scale) | Élevée | Élevé | Scale horizontal Kubernetes + load balancer |
| 3 | Nouvelle faille sécurité dans les dépendances | Élevée | Moyen | Snyk hebdomadaire + `poetry update` mensuel |
| 4 | Régression de l'API (breaking change) | Faible | Élevé | Versioning API (`/v1/validate`), tests d'intégration |
| 5 | Faux positifs (seuils trop bas) | Moyenne | Moyen | Seuils validés avec experts métier, ajustables |

---

## 8. Roadmap

```
Q2 2026 ─── MS6 stable en production
            - 0 vulnérabilité
            - Coverage 93%
            - Pipeline 4 jobs opérationnel

Q3 2026 ─── Seuils dynamiques
            - Chargement depuis un Config Service
            - Cache Redis pour les seuils
            - Rechargement à chaud sans redéploiement

Q4 2026 ─── Intégration Kafka
            - Consommateur Kafka en parallèle de l'API REST
            - Publication des résultats dans un topic "validated-readings"
            - Architecture alignée avec ms-analyse-trafic

Q1 2027 ─── Monitoring & Prédiction
            - Métriques Prometheus exposées
            - Tableau de bord Grafana dédié MS6
            - Prototype modèle prédictif (dépassements futurs)
```
