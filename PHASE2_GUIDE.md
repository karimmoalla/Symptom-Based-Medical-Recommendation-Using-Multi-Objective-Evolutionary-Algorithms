# PHASE 2 - Filtrage des Prestataires par Spécialité

## Vue D'ensemble

Vous avez maintenant un système complet à **2 phases** :

### **Phase 1 :** Extraction de la spécialité
- Analyse multilingue des symptômes
- Extrait les symptômes de la description du patient
- Recommande les 3 meilleures spécialités médicales pertinentes

### **Phase 2 :** Filtrage des prestataires  
- Filtre la base de données des 4 500 prestataires
- Retourne uniquement les prestataires specialisés dans la spécialité recommandée
- Trie par qualité, coût, ou délai d'attente

---

## Architecture

### Nouveaux fichiers créés :

1. **`src/specialty_mapper.py`**
   - Mappe les noms de spécialités aux IDs numériques des prestataires
   - Gère la correspondance automatique entre les deux bases de données

2. **`src/filtering.py`** (mise à jour)
   - Filtre les prestataires par spécialité
   - Récupère les meilleures options par qualité
   - Calcule les statistiques (prix moyen, délai d'attente, etc.)

3. **`src/pipeline.py`** (mise à jour)
   - Intègre le filtrage des prestataires dans le flux principal
   - Retourne les prestataires par spécialité

4. **`main.py`** (mise à jour)
   - Affiche les prestataires recommandés avec détails


### Fichiers modifiés :

- **`src/config.py`** : Ajout du chemin vers le fichier des prestataires
- **`src/pipeline.py`** : Intégration du ProviderFilter


---

## Utilisation

### Via la ligne de commande interactive :

```bash
python main.py
```

Exemple d'interaction :
```
Décrivez vos symptômes (ou 'q' pour quitter) :
> J'ai une forte douleur à la tête et des vertiges

Âge du patient (optionnel, appuyez sur Entrée) :
> 35

Est-ce une urgence ? (y/n) :
> n

Entrées supplémentaires disponibles :
- `Budget maximum en €` (optionnel) : permet de filtrer les prestataires dont le coût moyen dépasse ce montant.
- `Localisation` (ville/zone, optionnel) : priorise les prestataires proches lorsque l'information est disponible.

Poids par défaut pour la combinaison qualité/coût/proximité : `quality=0.5`, `cost=0.3`, `proximity=0.2`.
Si vous utilisez l'API Python directe, ces poids peuvent être fournis à `recommender.predict(...)`, sinon `main.py` applique les valeurs par défaut.

===================================================
--- PHASE 1 : ANALYSE DES SYMPTÔMES ---
===================================================
✅ Symptômes détectés : headache, dizziness

--- SPÉCIALITÉS RECOMMANDÉES (TOP 3) ---
  📍 Neurologist              : 85% de pertinence
  📍 Internal Medicine        : 45% de pertinence
  📍 Cardiologist             : 30% de pertinence

===================================================
--- PHASE 2 : PRESTATAIRES RECOMMANDÉS ---
===================================================

🏥 Neurologist
   (127 prestataires disponibles)
   ────────────────────────────────
   1. Dr. Jean Dupont
      ⭐ Qualité: 4.8/5 | ⏱️ Attente: 2 jours | 💰 Coût: 75€

   2. Clinique Saint-Louis
      ⭐ Qualité: 4.6/5 | ⏱️ Attente: 3 jours | 💰 Coût: 85€

   3. Dr. Marie Rousseau
      ⭐ Qualité: 4.5/5 | ⏱️ Attente: 1 jour | 💰 Coût: 65€
```

### Via Python :

```python
from src.pipeline import MedicalRecommender

recommender = MedicalRecommender()
recommender.load_data()

# Prédiction avec symptômes
result = recommender.predict(
    text="headache and dizziness",
    age=35,
    urgent=False
)

# Accéder aux résultats
print("Symptômes détectés:", result['detected_symptoms'])
print("Spécialités recommandées:", result['recommendations'])

# Providers trouvés par spécialité
for specialty, providers_df in result['providers'].items():
    print(f"\n{specialty}:")
    print(providers_df[['provider_name', 'quality_score', 'waiting_time_days', 'average_cost']])
```

### Pour obtenir les prestataires d'une spécialité spécifique :

```python
from src.pipeline import MedicalRecommender

recommender = MedicalRecommender()
recommender.load_data()

# Obtenir les 10 meilleurs cardiologues triés par qualité
cardiologists = recommender.get_providers_for_specialty(
    specialty='Cardiologist',
    top_n=10,
    sort_by='quality_score'  # ou 'waiting_time_days', 'average_cost'
)

print(cardiologists[['provider_name', 'quality_score', 'average_cost']])
```

---

## Structure des données

### Entrée (Symptômes du patient) :
- Texte libre en français ou anglais
- Âge optionnel
- Flag urgence (optionnel)

### Sortie (Résultats) :
- Symptômes détectés
- Top 3 spécialités recommandées avec scores
- Pour chaque spécialité : top 5 prestataires avec :
  - Nom du prestataire
  - Score de qualité (0-5)
  - Délai d'attente (jours)
  - Coût moyen (€)

---

## Options de tri pour les prestataires

- **`quality_score`** (défaut) : Meilleurs scores de qualité
- **`waiting_time_days`** : Délais d'attente les plus courts
- **`average_cost`** : Coûts les moins élevés

---

## Points clés

✅ Le système mappe automatiquement les spécialités aux IDs numériques  
✅ Fuzzy matching pour gérer les variations de noms  
✅ Support multilingue (français, anglais, etc.)  
✅ Filtrage intelligent basé sur le profil du patient (âge, urgence)  
✅ Statistiques disponibles par spécialité  

---

## Prochaines améliorations possibles

1. Créer une vraie table de correspondance spécialités ↔ IDs (si disponible)
2. Intégrer la géolocalisation pour les prestataires proches
3. Ajouter les avis patients en temps réel
4. Intégrer les tarifs d'assurance maladie
5. Historique des patients
