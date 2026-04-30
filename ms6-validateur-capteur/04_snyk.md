# Analyse Snyk — MS6 Validateur de Données Capteur

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Résultats avant corrections](#2-résultats-avant-corrections)
3. [Détail des vulnérabilités](#3-détail-des-vulnérabilités)
4. [Résultats après corrections](#4-résultats-après-corrections)
5. [Processus de correction](#5-processus-de-correction)
6. [Impact résumé](#6-impact-résumé)

---

## 1. Introduction

| Élément | Valeur |
|---|---|
| Outil | Snyk CLI (snyk.io) |
| Version | 1.1301.2 |
| Organisation | `geraldinefrancois` |
| Objectif | Détecter les vulnérabilités dans les dépendances Python |
| Fichier analysé | `poetry.lock` |
| Package manager | `poetry` |
| Intégration | Job `quality` du pipeline CI/CD `ms6-validateur.yml` |

Snyk analyse les dépendances déclarées dans `poetry.lock` (directes et transitives) et les compare à sa base de CVE. Les rapports sont conservés dans `snyk_avant.txt` et `snyk_apres.txt`.

---

## 2. Résultats avant corrections

```
Tested 25 dependencies for known issues, found 9 issues, 10 vulnerable paths.
```

### Tableau récapitulatif

| Paquet | Version vulnérable | Version corrigée | Sévérité | Snyk ID |
|---|---|---|---|---|
| `requests` | 2.25.0 | 2.33.0 | MEDIUM ×4 | SNYK-PYTHON-REQUESTS-10305723 |
| `requests` | 2.25.0 | 2.33.0 | MEDIUM | SNYK-PYTHON-REQUESTS-15763443 |
| `requests` | 2.25.0 | 2.33.0 | MEDIUM | SNYK-PYTHON-REQUESTS-5595532 |
| `requests` | 2.25.0 | 2.33.0 | MEDIUM | SNYK-PYTHON-REQUESTS-6928867 |
| `urllib3` | 1.26.20 | 2.6.3 | MEDIUM | SNYK-PYTHON-URLLIB3-10390194 |
| `urllib3` | 1.26.20 | 2.6.3 | HIGH | SNYK-PYTHON-URLLIB3-14192442 |
| `urllib3` | 1.26.20 | 2.6.3 | HIGH | SNYK-PYTHON-URLLIB3-14192443 |
| `urllib3` | 1.26.20 | 2.6.3 | HIGH | SNYK-PYTHON-URLLIB3-14896210 |
| `idna` | 2.10 | 3.13 | MEDIUM | SNYK-PYTHON-IDNA-6597975 |

---

## 3. Détail des vulnérabilités

### 3.1 requests@2.25.0 — 4 vulnérabilités MEDIUM

**Correction :** `poetry add requests==2.33.0`

| # | Titre | Sévérité | Snyk ID |
|---|---|---|---|
| 1 | Insertion of Sensitive Information Into Sent Data | MEDIUM | SNYK-PYTHON-REQUESTS-10305723 |
| 2 | Insecure Temporary File | MEDIUM | SNYK-PYTHON-REQUESTS-15763443 |
| 3 | Information Exposure | MEDIUM | SNYK-PYTHON-REQUESTS-5595532 |
| 4 | Always-Incorrect Control Flow Implementation | MEDIUM | SNYK-PYTHON-REQUESTS-6928867 |

**Impact :**
- **CVE-10305723** : Des données sensibles (headers d'authentification) peuvent être transmises à des redirections non sécurisées.
- **CVE-15763443** : Création de fichiers temporaires sans contrôle de permissions.
- **CVE-5595532** : Fuite d'informations via les headers HTTP lors des redirections.
- **CVE-6928867** : Mauvaise gestion du flux de contrôle pouvant contourner des validations.

---

### 3.2 urllib3@1.26.20 — 4 vulnérabilités (1 MEDIUM + 3 HIGH)

**Correction :** `poetry add urllib3>=2.6.3` (dépendance transitive de requests)

| # | Titre | Sévérité | Snyk ID |
|---|---|---|---|
| 1 | Open Redirect | MEDIUM | SNYK-PYTHON-URLLIB3-10390194 |
| 2 | Improper Handling of Highly Compressed Data (Data Amplification) | HIGH | SNYK-PYTHON-URLLIB3-14192442 |
| 3 | Allocation of Resources Without Limits or Throttling | HIGH | SNYK-PYTHON-URLLIB3-14192443 |
| 4 | Improper Handling of Highly Compressed Data (Data Amplification) | HIGH | SNYK-PYTHON-URLLIB3-14896210 |

**Impact :**
- **CVE-10390194** : Une URL malformée peut rediriger les requêtes vers un hôte arbitraire.
- **CVE-14192442/14896210** : Décompression de données malveillantes (zip bomb) pouvant épuiser la mémoire — vecteur de DoS.
- **CVE-14192443** : Absence de limite sur l'allocation mémoire lors du traitement de réponses HTTP volumineuses.

---

### 3.3 idna@2.10 — 1 vulnérabilité MEDIUM

**Correction :** `poetry add idna>=3.7` (dépendance transitive de requests)

| # | Titre | Sévérité | Snyk ID |
|---|---|---|---|
| 1 | Resource Exhaustion | MEDIUM | SNYK-PYTHON-IDNA-6597975 |

**Impact :** Le traitement de noms de domaine internationalisés (IDN) malformés peut provoquer une consommation excessive de CPU — vecteur de DoS via des requêtes DNS crafted.

---

## 4. Résultats après corrections

```
✔ Tested 25 dependencies for known issues, no vulnerable paths found.
```

### Versions corrigées

| Paquet | Avant | Après |
|---|---|---|
| `requests` | 2.25.0 | **2.33.0** |
| `urllib3` | 1.26.20 | **2.6.3** |
| `idna` | 2.10 | **3.13** |

**Statut : CONFORME**

---

## 5. Processus de correction

```
1. IDENTIFICATION
   snyk test --file=poetry.lock --package-manager=poetry
   → 9 issues détectées, 10 chemins vulnérables

2. ANALYSE
   Priorisation par sévérité : HIGH (3) → MEDIUM (6)
   Identification du package source : requests@2.25.0

3. MISE À JOUR
   poetry add requests==2.33.0
   → urllib3 migre automatiquement vers 1.26.20 (toujours vulnérable)

   poetry add urllib3>=2.6.3 idna>=3.7
   → toutes les dépendances transitives corrigées

4. VÉRIFICATION
   snyk test --file=poetry.lock --package-manager=poetry
   → 0 vulnérabilité confirmée
```

---

## 6. Impact résumé

| Métrique | Avant | Après |
|---|---|---|
| Total vulnérabilités | **9** | **0** |
| Sévérité HIGH | 3 | 0 |
| Sévérité MEDIUM | 6 | 0 |
| Chemins vulnérables | 10 | 0 |
| Dépendances auditées | 25 | 25 |
| Dépendances corrigées | — | 3 |
| Compliance | NON | **OUI** |
