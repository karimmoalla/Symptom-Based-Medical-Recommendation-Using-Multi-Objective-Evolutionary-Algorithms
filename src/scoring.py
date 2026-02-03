import pandas as pd
from typing import List, Dict, Tuple
from collections import defaultdict
from src.config import TARGET_COL

class SpecialtyScorer:
    def __init__(self, df: pd.DataFrame):
        """
        Initialise le moteur de scoring avec une analyse statistique de la base de données.
        """
        self.knowledge_base = self._build_knowledge_base(df)
        self.specialty_prevalence = df[TARGET_COL].value_counts(normalize=True).to_dict()
        
    def _build_knowledge_base(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Crée une matrice Symptôme -> {Spécialité: Probabilité}.
        On utilise ici une logique de spécificité pour réduire l'ambiguïté.
        """
        kb = defaultdict(lambda: defaultdict(int))
        feature_cols = [c for c in df.columns if c != TARGET_COL and 'Unnamed' not in c]
        
        # Groupement par maladie et somme des occurrences de symptômes
        grouped = df.groupby(TARGET_COL)[feature_cols].sum()
        
        for specialty in grouped.index:
            row = grouped.loc[specialty]
            for symptom, count in row.items():
                if count > 0:
                    # On stocke le nombre de fois où ce symptôme apparaît pour cette spécialité
                    kb[symptom][specialty] = float(count)
        
        return kb

    def score(self, symptoms: List[str], patient_age: int = None, is_urgent: bool = False) -> Dict[str, float]:
        """
        Calcule les scores avec pondération par spécificité et profil patient.
        """
        scores = defaultdict(float)
        
        if not symptoms:
            return {}

        for symptom in symptoms:
            if symptom in self.knowledge_base:
                matching_specialties = self.knowledge_base[symptom]
                
                # FACTEUR DE SPÉCIFICITÉ :
                # Si un symptôme n'apparaît que pour 1 spécialité, son poids est maximal (1.0).
                # S'il apparaît pour 10 spécialités, son poids est dilué (0.1).
                specificity_weight = 1.0 / len(matching_specialties)
                
                for specialty, count in matching_specialties.items():
                    # Score = (Fréquence dans la base) * (Spécificité du symptôme)
                    scores[specialty] += count * specificity_weight

        # AJUSTEMENT "DIAGNOSTIC DIFFÉRENTIEL" (Simulation)
        for spec in list(scores.keys()):
            # Exemple : Si le patient est jeune, on favorise légèrement la pédiatrie/médecine générale
            if patient_age and patient_age < 16:
                if 'Pediatrician' in spec: scores[spec] *= 1.5
            
            # Exemple : Si urgence détectée, on favorise la cardiologie ou médecine d'urgence
            if is_urgent:
                if 'Cardiologist' in spec: scores[spec] *= 2.0

        # Normalisation en pourcentage (0 à 100)
        total_score = sum(scores.values())
        if total_score > 0:
            final_scores = {k: round((v / total_score) * 100, 2) for k, v in scores.items()}
        else:
            final_scores = {}

        return final_scores

    def get_top_n(self, scores: Dict[str, float], n: int = 3) -> List[Tuple[str, float]]:
        """
        Retourne le Top N des spécialités triées par pertinence.
        """
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_scores[:n]