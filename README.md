# Système de Recommandation Médicale Intelligent (Phase 1)

Ce projet est un moteur d’aide à la décision médicale capable de transformer une description de symptômes en langage naturel en une recommandation de spécialités médicales optimisée.

## Fonctionnalités Clés ("Zéro Limite")

Pour éliminer les biais des systèmes classiques, ce moteur intègre des mécanismes avancés :

* **Extraction NLP Multilingue :** Utilisation de `deep-translator` pour supporter le Français et l'Anglais, couplé à `fuzzywuzzy` pour tolérer les fautes de frappe.
* **Intelligence Sémantique :** Un dictionnaire de mapping convertit le langage courant (ex: "vertiges") en terminologie médicale normalisée (ex: "dizziness").
* **Scoring Probabiliste Pondéré :** Le système calcule la pertinence d'une spécialité selon la **spécificité** du symptôme. Un symptôme rare (ex: jaunisse) a plus d'influence qu'un symptôme banal (ex: fatigue).
* **Diagnostic Différentiel Contextuel :** Intégration de l'âge et du niveau d'urgence pour ajuster les scores (ex: priorité automatique à la Cardiologie pour les urgences seniors).

---

##  Comment le code travaille (Pipeline Logique)

Le système suit un flux de données rigoureux pour garantir la précision du résultat :

1.  **Normalisation :** Traduction vers l'anglais et suppression des mots inutiles (*stop-words*) comme "je", "sens", "un peu".
2.  **Matching :** Recherche par mots-clés directs et par similarité de caractères dans la base de données `Specialist.xlsx`.
3.  **Calcul :** Le moteur de scoring attribue des points à chaque spécialité en fonction de la fréquence d'apparition du symptôme dans la littérature médicale.
4.  **Optimisation :** Application des bonus d'urgence et normalisation en pourcentages de confiance.



---

##  Scénarios de Test et Validation

| Input Utilisateur | Contexte | Résultat Attendu | Force du Code |
| :--- | :--- | :--- | :--- |
| *"J'ai des vertiges"* | Urgence: Oui | **Neurologist** | Mapping sémantique (Dizzy) |
| *"Yellow skin & stomach pain"* | Standard | **Hepatologist** | Poids de spécificité élevé |
| *"Chest pain"* | Âge: 70 / Urgent: Y | **Cardiologist** | Diagnostic différentiel actif |
| *"I feel itchy it's weird"* | Standard | **Dermatologist** | Filtrage du bruit textuel |

---

##  Installation et Utilisation

### 1. Prérequis
Python 3.8 ou supérieur.

### 2. Dépendances
Installez les bibliothèques nécessaires :
```bash
pip install pandas openpyxl deep-translator fuzzywuzzy python-Levenshtein