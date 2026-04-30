# Pipeline CI/CD DevSecOps — MS6 Validateur de Données Capteur

**Projet :** UrbanHub — EC03 Intégration et Déploiement Continu  
**Auteur :** MI202620  
**Date :** 2026-04-30  
**Fichier workflow :** `.github/workflows/ms6-validateur.yml`

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Job 1 — Test & Coverage](#2-job-1--test--coverage)
3. [Job 2 — Quality & Security](#3-job-2--quality--security)
4. [Job 3 — Build & Push Docker](#4-job-3--build--push-docker)
5. [Job 4 — Deploy Staging](#5-job-4--deploy-staging)
6. [Déclencheurs](#6-déclencheurs)
7. [Conclusion](#7-conclusion)

---

## 1. Introduction

Le pipeline CI/CD du microservice MS6 est implémenté via GitHub Actions. Il s'exécute en **4 jobs séquentiels** : chaque job ne démarre que si le précédent a réussi. Un échec à n'importe quelle étape bloque l'ensemble du pipeline (principe fail fast).

**Objectif :** Automatiser la vérification de la qualité du code, l'audit de sécurité, la construction de l'image Docker et le déploiement en staging à chaque modification du microservice.

**Architecture du pipeline :**

```
[push / pull_request]
        |
        v
  Job 1: test
        |
  needs: test
        v
  Job 2: quality
        |
  needs: quality
        v
  Job 3: build
        |
  needs: build
        v
  Job 4: deploy-staging
```

**Secrets GitHub requis :**

| Secret | Usage |
|---|---|
| `GHCR_TOKEN` | Authentification push/pull vers GitHub Container Registry |
| `SONAR_TOKEN` | Analyse qualité SonarCloud |
| `SNYK_TOKEN` | Audit des vulnérabilités Snyk |

---

## 2. Job 1 — Test & Coverage

**Nom :** `Tests & Coverage`  
**Runner :** `ubuntu-latest`  
**Working directory :** `ms6-validateur-capteur/`  
**Dépend de :** aucun (premier job)

### Installation des dépendances

```yaml
- name: Install Poetry
  run: pip install poetry

- name: Install dependencies
  run: poetry install --no-interaction
```

Poetry lit `pyproject.toml` et installe toutes les dépendances versionnées depuis `poetry.lock`. Cela garantit la reproductibilité exacte de l'environnement entre la machine locale et le runner CI.

Équivalent manuel :
```bash
pip install poetry
poetry install --no-interaction
```

### Exécution des tests

```yaml
- name: Run tests with coverage
  run: |
    poetry run pytest tests/ -v \
      --cov=src \
      --cov-report=xml \
      --cov-report=term
```

| Paramètre | Rôle |
|---|---|
| `tests/` | Répertoire contenant les tests |
| `-v` | Affichage détaillé (verbose) |
| `--cov=src` | Mesure la couverture du code dans `src/` |
| `--cov-report=xml` | Génère `coverage.xml` pour SonarCloud |
| `--cov-report=term` | Affiche le tableau de couverture dans les logs CI |

**Seuil de couverture :** 80% minimum requis. Un coverage inférieur bloque le pipeline.  
**Résultat mesuré :** 93% (11 tests passés).

### Rapports générés

| Fichier | Format | Usage |
|---|---|---|
| `coverage.xml` | XML (Cobertura) | Transmis à SonarCloud via artifact |
| `rapport_tests.xml` | JUnit XML | Exploitable par les dashboards CI/CD |
| `rapport_tests.txt` | Texte | Lisible humainement |

### Export de l'artifact

```yaml
- name: Upload coverage report
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: ms6-validateur-capteur/coverage.xml
```

`coverage.xml` est transmis au Job 2 via le système d'artifacts GitHub Actions, car les jobs s'exécutent sur des runners distincts et ne partagent pas de système de fichiers.

---

## 3. Job 2 — Quality & Security

**Nom :** `Quality & Security`  
**Runner :** `ubuntu-latest`  
**Working directory :** `ms6-validateur-capteur/`  
**Dépend de :** `test` (`needs: test`)

### 3.1 Flake8 — Linting Python

```yaml
- name: Flake8 lint
  continue-on-error: true
  run: |
    pip install flake8
    flake8 src/ tests/ | tee flake8_output.txt
```

| Paramètre | Valeur |
|---|---|
| Cibles | `src/` et `tests/` |
| `continue-on-error` | `true` — le pipeline ne s'arrête pas si des erreurs sont détectées |
| Sortie | `flake8_output.txt` (uploadé comme artifact) |

**Règles PEP8 vérifiées :**

| Code | Description |
|---|---|
| E501 | Ligne dépassant 79 caractères |
| E402 | Import hors position (pas en tête de fichier) |
| E303 | Plus de 2 lignes vides consécutives |

**Démarche AVANT / APRÈS :**

- AVANT : 3 erreurs détectées (E501 ×2 dans `validator.py`, E402 dans `test_validator.py`)
- APRÈS : 0 erreur après corrections (reformatage des lignes longues, réorganisation des imports)

Résultat consigné dans `flake8_avant.txt` et `flake8_apres.txt`.

### 3.2 SonarCloud — Analyse qualité

```yaml
- name: Download coverage report
  uses: actions/download-artifact@v4
  with:
    name: coverage-report
    path: ms6-validateur-capteur/

- name: SonarCloud scan
  if: ${{ secrets.SONAR_TOKEN != '' }}
  uses: SonarSource/sonarcloud-github-action@v3
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
  with:
    projectBaseDir: ms6-validateur-capteur
```

**Configuration** (`sonar-project.properties`) :

```properties
sonar.projectKey=GeraldineFrancois_UrbanHub-EC03
sonar.organization=geraldinefrancois
sonar.projectName=UrbanHub-EC03
sonar.projectVersion=1.0
sonar.sources=.
sonar.sourceEncoding=UTF-8
sonar.python.version=3.11
sonar.python.coverage.reportPaths=ms6-validateur-capteur/coverage.xml
```

| Paramètre | Rôle |
|---|---|
| `sonar.python.version` | Précise la version Python pour l'analyse (supprime le warning générique) |
| `sonar.python.coverage.reportPaths` | Chemin vers `coverage.xml` pour afficher la couverture dans le dashboard |
| `fetch-depth: 0` | Historique git complet requis par SonarCloud pour les analyses différentielles |

**Démarche AVANT / APRÈS :**

- AVANT : problèmes identifiés (utilisation de `datetime.utcnow()` dépréciée, lignes trop longues)
- APRÈS : 0 problème majeur, couverture 93% visible dans le dashboard SonarCloud

### 3.3 Snyk — Audit de sécurité des dépendances

```yaml
- name: Snyk security scan
  continue-on-error: true
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  run: |
    npm install -g snyk
    snyk test --file=poetry.lock --package-manager=poetry | tee snyk_report.txt
```

| Paramètre | Valeur |
|---|---|
| `--file=poetry.lock` | Analyse le lock file Poetry (dépendances directes et transitives) |
| `--package-manager=poetry` | Précise le gestionnaire pour l'interprétation correcte du lock file |
| `continue-on-error` | `true` — le rapport est généré même si des vulnérabilités sont trouvées |
| Sortie | `snyk_report.txt` (uploadé comme artifact) |

**Démarche AVANT / APRÈS :**

| Métrique | Avant | Après |
|---|---|---|
| Vulnérabilités totales | 9 | 0 |
| Sévérité HIGH | 3 | 0 |
| Sévérité MEDIUM | 6 | 0 |
| Packages corrigés | — | `requests` 2.33.0, `urllib3` 2.6.3, `idna` 3.13 |

Rapports conservés : `snyk_avant.txt` (état initial) et `snyk_apres.txt` (état final).

---

## 4. Job 3 — Build & Push Docker

**Nom :** `Build & Push Docker`  
**Runner :** `ubuntu-latest`  
**Dépend de :** `quality` (`needs: quality`)  
**Permissions :** `packages: write`

### Authentification GHCR

```yaml
- name: Log in to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GHCR_TOKEN }}
```

`GHCR_TOKEN` est un Personal Access Token GitHub configuré dans les secrets du dépôt avec les permissions `read:packages` et `write:packages`.

### Construction et tagging de l'image

```yaml
- name: Build Docker image
  run: |
    docker build \
      -t ${{ env.IMAGE }}:${{ github.sha }} \
      -t ${{ env.IMAGE }}:latest \
      ms6-validateur-capteur/
```

**Convention de nommage :**

```
ghcr.io/geraldinefrancois/urbanhub/ms6-validateur:[TAG]
```

| Tag | Usage |
|---|---|
| `${{ github.sha }}` | SHA du commit — identifiant unique, immuable, traçable |
| `latest` | Dernière version stable, utilisée par docker-compose |

### Publication sur GHCR

```yaml
- name: Push Docker image
  run: |
    docker push ${{ env.IMAGE }}:${{ github.sha }}
    docker push ${{ env.IMAGE }}:latest
```

Les deux tags sont poussés indépendamment. Le tag SHA permet un rollback précis vers n'importe quelle version antérieure.

### Dockerfile (base image et exposition du port)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-interaction --no-ansi

COPY src/ ./src/

EXPOSE 8006

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8006/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8006"]
```

---

## 5. Job 4 — Deploy Staging

**Nom :** `Deploy & Smoke Test Staging`  
**Runner :** `ubuntu-latest`  
**Dépend de :** `build` (`needs: build`)  
**Permissions :** `packages: read`

### Démarrage du container

```yaml
- name: Start container
  run: |
    docker run -d \
      --name ms6-staging \
      -p 8006:8006 \
      ${{ env.IMAGE }}:${{ github.sha }}
```

| Paramètre | Valeur |
|---|---|
| `-d` | Mode détaché (background) |
| `-p 8006:8006` | Port hôte 8006 → port container 8006 |
| Tag utilisé | SHA du commit courant (image exacte du build précédent) |

### Health check

```yaml
- name: Wait for startup
  run: sleep 2

- name: Health check
  run: curl -f http://localhost:8006/health
```

`curl -f` retourne un code d'erreur non nul si la réponse HTTP est >= 400. Si `/health` ne répond pas ou retourne une erreur, le job échoue et le pipeline est bloqué.

Réponse attendue :
```json
{"status": "healthy", "service": "ms6-validateur"}
```

### Nettoyage

```yaml
- name: Stop container
  if: always()
  run: docker stop ms6-staging
```

`if: always()` garantit que le container est stoppé même si le health check a échoué, évitant de laisser des ressources orphelines sur le runner.

### Configuration docker-compose (référence)

```yaml
ms6-validateur:
  image: ghcr.io/geraldinefrancois/urbanhub/ms6-validateur:latest
  container_name: ms6-validateur
  ports:
    - "8006:8006"
  networks:
    - urbanhub-net
```

---

## 6. Déclencheurs

### Branches surveillées

```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

| Événement | Branches | Effet |
|---|---|---|
| `push` | `main`, `develop` | Pipeline complet déclenché |
| `pull_request` | `main`, `develop` | Pipeline complet déclenché (vérification avant merge) |

### Filtres de chemin

```yaml
paths:
  - 'ms6-validateur-capteur/**'
  - '.github/workflows/ms6-validateur.yml'
```

Le pipeline ne s'exécute que si les fichiers modifiés appartiennent au microservice MS6 ou au fichier workflow lui-même. Une modification dans `ms-auth/` ou `ms-analyse-trafic/` ne déclenche pas ce pipeline.

---

## 7. Conclusion

Le pipeline CI/CD du MS6 implémente une approche DevSecOps complète en 4 jobs séquentiels :

| Job | Rôle | Bloquant |
|---|---|---|
| `test` | Valide le comportement du code (11 tests, coverage 93%) | Oui |
| `quality` | Vérifie la qualité (flake8, SonarCloud) et la sécurité (Snyk, 0 CVE) | Oui |
| `build` | Construit et publie l'image Docker sur GHCR | Oui |
| `deploy-staging` | Vérifie que le service démarre et répond correctement | Oui |

Chaque job s'appuie sur le succès du précédent. Un échec arrête immédiatement le pipeline et empêche la progression vers les étapes suivantes. Cette approche garantit qu'aucune image défectueuse ou vulnérable n'est publiée sur le registre.
