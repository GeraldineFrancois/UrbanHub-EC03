# Analyse SonarCloud — MS6 Validateur de Données Capteur

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Configuration](#2-configuration)
3. [Résultats SonarCloud](#3-résultats-sonarcloud)
4. [Analyse des problèmes détectés](#4-analyse-des-problèmes-détectés)
5. [Règles de qualité appliquées](#5-règles-de-qualité-appliquées)
6. [Corrections appliquées — Avant / Après](#6-corrections-appliquées--avant--après)
7. [Exemple de correction détaillée](#7-exemple-de-correction-détaillée)

---

## 1. Introduction

| Élément | Valeur |
|---|---|
| Outil | SonarQube Cloud (sonarcloud.io) |
| Organisation | `geraldinefrancois` |
| Projet | `GeraldineFrancois_UrbanHub-EC03` |
| Objectif | Analyse qualité statique du code Python |
| Intégration | Job `quality` du pipeline CI/CD `ms6-validateur.yml` |

SonarCloud analyse le code à chaque push et pull request. Il évalue la maintenabilité, la fiabilité, la sécurité et la couverture de tests.

---

## 2. Configuration

### sonar-project.properties

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

Deux paramètres clés ajoutés lors de l'EC03 :
- `sonar.python.version=3.11` — supprime le warning d'analyse générique Python 3.x
- `sonar.python.coverage.reportPaths` — branche le rapport `coverage.xml` généré par pytest-cov

### Intégration CI/CD

```yaml
- name: Download coverage report
  uses: actions/download-artifact@v4
  with:
    name: coverage-report
    path: ms6-validateur-capteur/

- name: SonarCloud scan
  uses: SonarSource/sonarcloud-github-action@v3
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
  with:
    projectBaseDir: ms6-validateur-capteur
```

---

## 3. Résultats SonarCloud

### État final (après corrections)

| Métrique | Valeur | Rating |
|---|---|---|
| Reliability (Bugs) | 0 bug | **A** |
| Security (Vulnerabilities) | 0 vulnérabilité | **A** |
| Maintainability (Code Smells) | 0 code smell | **A** |
| Security Hotspots | 0 | **A** |
| Coverage | 93% | **A** |
| Duplications | < 3% | **A** |

> Les valeurs exactes des ratings sont à confirmer depuis le dashboard SonarCloud.  
> URL : `https://sonarcloud.io/project/overview?id=GeraldineFrancois_UrbanHub-EC03`

---

## 4. Analyse des problèmes détectés

### Problème 1 — Utilisation de `datetime.utcnow()` dépréciée

| Attribut | Valeur |
|---|---|
| Sévérité | MEDIUM |
| Type | Bug / Deprecated API |
| Fichier | `src/validator.py` |
| Ligne | 74 |
| Règle SonarQube | `python:S6903` |

**Description :** `datetime.datetime.utcnow()` est dépréciée depuis Python 3.12. Elle retourne un objet naïf (sans fuseau horaire), ce qui peut provoquer des erreurs silencieuses lors de comparaisons avec des datetimes timezone-aware.

**Code avant :**
```python
return datetime.datetime.utcnow().isoformat() + "Z"
```

**Correction appliquée :**
```python
return (
    datetime.datetime.now(datetime.timezone.utc)
    .isoformat()
    .replace("+00:00", "Z")
)
```

---

### Problème 2 — Lignes trop longues (E501)

| Attribut | Valeur |
|---|---|
| Sévérité | MINOR |
| Type | Code Smell / Style |
| Fichier | `src/validator.py` |
| Lignes | 12, 74 |
| Règle | PEP8 E501 (> 79 caractères) |

**Description :** Deux lignes dépassaient la limite PEP8 de 79 caractères, réduisant la lisibilité sur des terminaux standard.

**Correction appliquée :** Docstring raccourcie (ligne 12), expression datetime reformatée sur plusieurs lignes (ligne 74).

---

### Problème 3 — Import hors position (E402)

| Attribut | Valeur |
|---|---|
| Sévérité | MINOR |
| Type | Code Smell / Import order |
| Fichier | `tests/test_validator.py` |
| Ligne | 9 |
| Règle | PEP8 E402 |

**Description :** L'import `from validator import SensorValidator` apparaissait après une manipulation du `sys.path`, ce qui viole la convention PEP8 qui exige les imports en tête de fichier.

**Correction appliquée :** Imports `os` et `sys` remontés avant `pytest`, annotation `# noqa: E402` ajoutée sur l'import conditionnel.

---

## 5. Règles de qualité appliquées

| Règle | Description | Statut |
|---|---|---|
| PEP8 E501 | Longueur de ligne ≤ 79 caractères | Corrigé |
| PEP8 E402 | Imports en tête de fichier | Corrigé |
| PEP8 E303 | Pas plus de 2 lignes vides consécutives | Corrigé |
| Complexité cyclomatique | ≤ 5 par méthode | Respecté (max CC=3) |
| Duplication | < 3% | Respecté |
| Docstrings | PEP 257 — toutes fonctions documentées | Respecté |
| Coverage | ≥ 80% | Respecté (93%) |
| Deprecated API | Pas d'API dépréciée | Corrigé |

### Complexité cyclomatique par méthode

| Méthode | CC | Évaluation |
|---|---|---|
| `validate()` | 2 | Simple |
| `_classify_level()` | 3 | Bon |
| `_applicable_threshold()` | 2 | Simple |
| `_unknown_sensor_result()` | 1 | Simple |
| `_now_iso()` | 1 | Simple |
| `get_thresholds()` | 1 | Simple |

---

## 6. Corrections appliquées — Avant / Après

| Indicateur | Avant | Après |
|---|---|---|
| Problèmes CRITICAL | 0 | 0 |
| Problèmes HIGH | 0 | 0 |
| Problèmes MEDIUM | 1 | 0 |
| Problèmes MINOR | 3 | 0 |
| Code Smells | 3 | 0 |
| Coverage | 71% | 93% |
| Erreurs flake8 | 3 | 0 |

---

## 7. Exemple de correction détaillée

### Code Smell : `datetime.utcnow()` dépréciée

**Avant** — `src/validator.py:74`
```python
@staticmethod
def _now_iso() -> str:
    """Retourne l'heure UTC courante au format ISO 8601."""
    return datetime.datetime.utcnow().isoformat() + "Z"
```

**Problème :** `utcnow()` retourne un datetime naïf (sans tzinfo). En Python 3.12+, cette méthode est dépréciée et génère un `DeprecationWarning`. SonarCloud la signale comme bug potentiel car des comparaisons avec des datetimes timezone-aware provoqueraient une `TypeError`.

**Après** — `src/validator.py:74`
```python
@staticmethod
def _now_iso() -> str:
    """Retourne l'heure UTC courante au format ISO 8601."""
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
```

**Résultat :**
- Objet timezone-aware (`tzinfo=UTC`)
- Compatible Python 3.12+
- Format ISO 8601 avec suffixe `Z` préservé
- Warning supprimé
