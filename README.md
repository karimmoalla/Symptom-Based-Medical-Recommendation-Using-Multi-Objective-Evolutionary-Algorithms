```markdown
#  Projet Recommandation Médicale - Phase 1

Ce projet implémente la première phase d'un système d'orientation médicale intelligent, visant à transformer une plainte patient en une recommandation de spécialité médicale.

##  Analyse de la Base de Données (`Specialist.xlsx`)
La base de données sert de **matrice de connaissances**. 
- **Dimensions :** 4920 cas cliniques x 133 colonnes.
- **Logique :** Variables binaires (0/1) représentant la présence de symptômes corrélés à une étiquette `Disease` (Spécialité).

##  Architecture du Code & Réflexion
Le système est découpé en modules pour garantir la robustesse de l'extraction :

### 1. `config.py` (Centralisation)
* **Rôle :** Paramétrage global.
* **Réflexion :** Garantit la portabilité du projet (changement facile de source de données).

### 2. `preprocessing.py` (Nettoyage)
* **Rôle :** Normalisation du texte (minuscules, retrait accents/ponctuation).
* **Réflexion :** Réduire le "bruit" pour ne garder que l'essence sémantique.

### 3. `extraction.py` (Moteur NLP Robuste)
* **Logique :** Traduction automatique -> Dictionnaire de synonymes -> Fuzzy Matching (Algorithme de Levenshtein).
* **Réflexion :** Tolérance maximale aux erreurs humaines et gestion du multilingue (FR/EN).



### 4. `scoring.py` (Moteur de Décision)
* **Formule :** $Score(Spécialité) = \sum Poids(SymptômesDetected)$
* **Réflexion :** La décision est basée sur la probabilité statistique issue de l'analyse globale de la base de données.

### 5. `pipeline.py` (Orchestrateur)
* **Rôle :** Relie les modules pour transformer un "Input Brut" en "Top 3 Spécialités".

---
##  Vers la Phase 4 (Optimisation NSGA-II)
Cette Phase 1 est cruciale pour le futur algorithme génétique. En filtrant avec précision la spécialité médicale, elle définit l'espace de recherche restreint dans lequel le **NSGA-II** pourra optimiser les objectifs de **coût, distance et temps d'attente**.

## Usage

Pour lancer l'interface interactive (recommandé pour un utilisateur non technique) :

```bash
python main.py
```

Entrées demandées :
- `symptoms` : description libre des symptômes (français ou anglais)
- `age` : âge du patient (optionnel)
- `urgent` : `y` ou `n` (optionnel)
- `budget` : budget maximum en € (optionnel)
- `location` : ville/zone (optionnel)

Poids par défaut (combinaison qualité/coût/proximité) : `quality=0.5`, `cost=0.3`, `proximity=0.2`.

Remarque : pour un usage programmatique, appelez `MedicalRecommender.predict(...)` et fournissez `budget`, `location` et les poids si nécessaire.
```
