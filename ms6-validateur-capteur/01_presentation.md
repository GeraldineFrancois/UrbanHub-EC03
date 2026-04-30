# MS6 — Validateur de Données Capteur

**Projet :** UrbanHub — EC03 Intégration et Déploiement Continu
**Auteur :** MI202620
**Date :** 2026-04-30
**Branche :** `feature/ms6-validateur-ec03`

---

## Table des matières

1. [Rôle du validateur dans l'architecture UrbanHub](#1-rôle-du-validateur-dans-larchitecture-urbanhub)
2. [Positionnement dans la chaîne de traitement](#2-positionnement-dans-la-chaîne-de-traitement)
3. [Lien avec les exigences BC01](#3-lien-avec-les-exigences-bc01)
4. [Technologies utilisées](#4-technologies-utilisées)
5. [Prérequis pour exécution locale](#5-prérequis-pour-exécution-locale)

---

## 1. Rôle du validateur dans l'architecture UrbanHub

MS6 est un microservice de validation des mesures capteur. Son rôle est de recevoir une mesure brute (type de capteur + valeur numérique), de la comparer à des seuils de référence, et de retourner une classification normalisée indiquant si la mesure est dans un état normal, modéré ou critique.

Le validateur ne stocke pas de données et ne prend pas de décision métier. Il produit exclusivement un résultat de classification exploitable par les services en aval. Cette responsabilité unique — valider et classifier — délimite son périmètre et garantit sa substituabilité dans l'architecture globale.

Les quatre types de capteurs supportés sont :

| Capteur | Seuil modéré | Seuil critique | Unité |
|---|---|---|---|
| CO2 (`co2`) | 800 | 1000 | ppm |
| Température (`temperature`) | 35 | 40 | °C |
| Bruit (`noise`) | 70 | 85 | dB |
| Particules fines (`pm25`) | 25 | 50 | µm/m³ |

La logique de classification produit quatre niveaux :

- `normal` — valeur inférieure au seuil modéré, mesure valide
- `moderate` — valeur entre le seuil modéré et le seuil critique, mesure valide
- `critical` — valeur supérieure ou égale au seuil critique, mesure invalide
- `unknown` — capteur non répertorié, mesure invalide

---

## 2. Positionnement dans la chaîne de traitement

MS6 s'insère entre la collecte brute et le traitement analytique des données capteur.

**Flux de données :**

```
Capteurs IoT
    |
    | données brutes (protocole MQTT)
    v
MS Collecte IoT  (ms-collecte-iot — port 8002)
    |
    | POST /validate  {"sensor": "co2", "value": 850.0}
    v
MS6 Validateur  (ms6-validateur-capteur — port 8000)
    |
    | {"valid": true, "level": "moderate", "threshold": 800.0, "timestamp": "..."}
    v
MS Analyse Trafic  (ms-analyse-trafic — port 8003)
    |
    v
MS Alerte  (ms-alerte — port 8004)
```

MS Collecte IoT est responsable de la réception des trames MQTT et de leur normalisation. Il délègue la qualification de chaque mesure à MS6 via un appel HTTP synchrone sur `POST /validate`. MS6 répond avec la classification et le seuil applicable. MS Analyse Trafic consomme ensuite les données enrichies pour produire des agrégats ou déclencher des événements vers MS Alerte.

MS6 ne connaît pas ses consommateurs. Il expose une interface REST standard, ce qui autorise tout service à l'interroger sans modification.

---

## 3. Lien avec les exigences BC01

BC01 définit les principes architecturaux du système d'information UrbanHub. MS6 les applique de la manière suivante.

**Découplage**

MS6 est un service indépendant, déployé et versionné séparément des autres microservices. Son contrat d'interface — `POST /validate` avec un payload JSON standardisé — ne dépend d'aucun autre service. La suppression ou le remplacement de MS6 n'impacte pas les autres composants tant que le contrat est respecté.

**Scalabilité**

Le service est stateless : chaque requête est traitée de manière autonome sans état partagé entre les instances. Il est possible de déployer plusieurs instances en parallèle derrière un load balancer sans coordination inter-instances. L'image Docker publiée sur GHCR permet un déploiement horizontal immédiat sous Kubernetes ou Docker Compose.

**Sécurité**

Les dépendances sont auditées avec Snyk à chaque exécution du pipeline CI/CD. Le passage de 9 vulnérabilités (état initial) à 0 (état final) a été documenté et versionné. L'image Docker utilise `python:3.11-slim` pour réduire la surface d'attaque. Les secrets (tokens SonarCloud, Snyk, GHCR) sont gérés exclusivement via GitHub Secrets et ne sont jamais exposés dans le code.

**Architecture événementielle**

Dans l'architecture actuelle, MS6 fonctionne en mode synchrone HTTP. La conception de `SensorValidator` est découplée du transport : la méthode `validate()` prend un capteur et une valeur en entrée et retourne un dictionnaire, sans dépendance à FastAPI. Cette structure permet d'intégrer ultérieurement un consommateur Kafka sans modifier la logique métier, en suivant le pattern adopté par `ms-analyse-trafic`.

---

## 4. Technologies utilisées

### Langage et framework

| Composant | Technologie | Version |
|---|---|---|
| Langage | Python | 3.11 |
| Framework web | FastAPI | 0.136.1 |
| Serveur ASGI | Uvicorn | 0.46.0 |
| Validation des données | Pydantic | 2.13.3 |
| Gestionnaire de dépendances | Poetry | 2.x |

### Dépendances de test et qualité

| Outil | Version | Rôle |
|---|---|---|
| pytest | 9.0.3 | Exécution des tests |
| pytest-cov | 7.1.0 | Rapport de couverture |
| httpx | 0.28.1 | Client HTTP pour TestClient FastAPI |
| flake8 | latest | Linting PEP8 |

### Dépendances corrigées (audit Snyk)

| Paquet | Version initiale | Version corrigée | Raison |
|---|---|---|---|
| requests | 2.25.0 | 2.33.0 | 4 CVE Medium |
| urllib3 | 1.26.20 | 2.6.3 | 3 CVE High, 1 CVE Medium |
| idna | 2.10 | 3.13 | 1 CVE Medium |

### Infrastructure

| Composant | Technologie |
|---|---|
| Containerisation | Docker (`python:3.11-slim`) |
| Registre d'images | GitHub Container Registry (GHCR) |
| CI/CD | GitHub Actions |
| Analyse qualité | SonarCloud |
| Audit sécurité | Snyk CLI 1.1301.2 |

---

## 5. Prérequis pour exécution locale

### Système d'exploitation

Compatible Linux, macOS et Windows (WSL2 recommandé pour Docker sous Windows).

### Outils requis

| Outil | Version minimale | Commande de vérification |
|---|---|---|
| Python | 3.11 | `python --version` |
| Poetry | 1.8 | `poetry --version` |
| Git | 2.x | `git --version` |
| Docker | 24.x | `docker --version` |
| Docker Compose | 2.x | `docker compose version` |

### Installation de Poetry

```bash
pip install poetry
```

### Cloner et initialiser le projet

```bash
git clone https://github.com/GeraldineFrancois/UrbanHub-EC03.git
cd UrbanHub-EC03
git checkout feature/ms6-validateur-ec03
cd ms6-validateur-capteur
poetry install
```

### Ports utilisés

| Service | Port | Usage |
|---|---|---|
| MS6 Validateur | 8006 | API REST principale |
| Swagger UI | 8006 | Documentation interactive (`/docs`) |

Les seuils sont définis statiquement dans `src/config.py`.

Pour le pipeline CI/CD, les secrets suivants doivent être configurés dans GitHub Settings > Secrets :

| Secret | Usage |
|---|---|
| `GHCR_TOKEN` | Push de l'image Docker vers GHCR |
| `SONAR_TOKEN` | Analyse SonarCloud |
| `SNYK_TOKEN` | Audit des dépendances Snyk |

### Lancer le service

```bash
# Mode développement (rechargement automatique)
poetry run uvicorn src.main:app --reload --port 8006

# Vérification
curl http://localhost:8006/health
```
