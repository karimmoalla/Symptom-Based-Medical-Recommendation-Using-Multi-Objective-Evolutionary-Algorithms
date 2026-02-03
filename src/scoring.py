import pandas as pd
from typing import List, Dict, Tuple
from collections import defaultdict
from src.config import TARGET_COL

class SpecialtyScorer:
    def __init__(self, df: pd.DataFrame):
        """
        Builds the scoring model from the dataframe.
        """
        self.knowledge_base = self._build_knowledge_base(df)
        
    def _build_knowledge_base(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Create a map: Symptom -> {Specialty: Frequency/Score}
        """
        kb = defaultdict(lambda: defaultdict(int))
        
        # Assume columns are valid symptoms if they are not the target
        # and values are binary or numeric.
        feature_cols = [c for c in df.columns if c != TARGET_COL and c != 'Unnamed: 0']
        
        # We can aggregate: for each symptom, count how many times it appears for each specialty
        # This might be slow if iterating rows.
        # Vectorized approach:
        # Group by Specialty, sum symptoms.
        
        # Check if values are numeric (0/1)
        # If the dataset is large, this is efficient.
        try:
            grouped = df.groupby(TARGET_COL)[feature_cols].sum()
            # grouped index = Specialty
            # grouped columns = Symptoms
            # values = count of times symptom appeared for that specialty
            
            # Convert to dictionary structure
            # kb[symptom][specialty] = count
            for specialty in grouped.index:
                row = grouped.loc[specialty]
                for symptom, count in row.items():
                    if count > 0:
                        kb[symptom][specialty] = float(count)
                        
            # Normalize? (Optional)
            # P(Specialty | Symptom) ~ Count(S, Sp) / Count(S)
            # For now, raw counts act as weights. Common associations have higher scores.
            
        except Exception as e:
            print(f"Error building knowledge base: {e}")
            # Fallback (if data is not numeric?)
            pass
            
        return kb

    def score(self, symptoms: List[str]) -> Dict[str, float]:
        """
        Calculate scores for all updated specialties based on input symptoms.
        """
        scores = defaultdict(float)
        
        for symptom in symptoms:
            if symptom in self.knowledge_base:
                specialty_weights = self.knowledge_base[symptom]
                for specialty, weight in specialty_weights.items():
                    scores[specialty] += weight
                    
        return dict(scores)

    def get_top_n(self, scores: Dict[str, float], n: int = 3) -> List[Tuple[str, float]]:
        """
        Return top N specialties.
        """
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_scores[:n]
