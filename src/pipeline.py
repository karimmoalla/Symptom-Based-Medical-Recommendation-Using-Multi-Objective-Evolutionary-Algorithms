import pandas as pd
import os
from src.config import SPECIALIST_FILE, TARGET_COL, K2_PROVIDERS_FILE
from src.preprocessing import normalize_text
from src.extraction import SymptomExtractor
from src.k1_brain import K1Brain
from src.filtering import ProviderFilter

class MedicalRecommender:
    def __init__(self):
        self.df = None
        self.extractor = None
        self.scorer = None
        self.provider_filter = None
        self.is_ready = False

    def load_data(self):
        try:
            # Instantiate K1Brain which loads the intelligence (RF weights, IDF, Tree)
            self.scorer = K1Brain()
            
            # The full list of symptoms is available via the IDF weights extracted in K1Brain
            symptom_cols = list(self.scorer.idf_weights.keys())
            self.extractor = SymptomExtractor(symptom_cols)

            # Charger les prestataires
            if os.path.exists(K2_PROVIDERS_FILE):
                self.provider_filter = ProviderFilter(K2_PROVIDERS_FILE, SPECIALIST_FILE)
            
            self.is_ready = True
        except Exception as e:
            self.is_ready = False

    def predict(self, text: str, age: int = None, urgent: bool = False, top_n: int = 3,
                budget: float = None, location: str = None,
                weight_quality: float = 0.5, weight_cost: float = 0.3, weight_proximity: float = 0.2):
        if not self.is_ready:
            return {"error": "System not initialized."}

        # 1. Extraction intelligente (gère la négation et la langue)
        detected_symptoms = self.extractor.extract(text)
        
        # 2. Scoring avancé (gère la spécificité et le profil patient)
        # On passe l'âge et l'urgence au scorer
        scores = self.scorer.score(detected_symptoms, patient_age=age, is_urgent=urgent)
        
        # 3. Formatage des résultats
        top_results = self.scorer.get_top_n(scores, top_n)
        
        # 4. Filtrage des prestataires (PHASE 2)
        providers_by_specialty = {}
        top_specialty_providers = None
        
        if self.provider_filter:
            specialties = [spec for spec, _ in top_results]
            
            providers_by_specialty = self.provider_filter.get_top_providers(
                specialties,
                top_n=5,
                sort_by='quality_score',
                budget=budget,
                location=location,
                weight_quality=weight_quality,
                weight_cost=weight_cost,
                weight_proximity=weight_proximity
            )
            # Also compute top providers for the top specialty using NSGA2
            if len(top_results) > 0:
                top_spec = top_results[0][0]
                try:
                    top_specialty_providers = self.provider_filter.optimize_providers_nsga(
                        top_spec, top_k=3, budget=budget, location=location
                    )
                except Exception:
                    top_specialty_providers = None
        
        return {
            "input_text": text,
            "detected_symptoms": detected_symptoms,
            "recommendations": top_results,
            "patient_context": {"age": age, "urgent": urgent, "budget": budget, "location": location,
                                "weights": {"quality": weight_quality, "cost": weight_cost, "proximity": weight_proximity}},
            "providers": providers_by_specialty,
            "top_specialty_providers": top_specialty_providers
        }
    
    def get_providers_for_specialty(self, specialty: str, top_n: int = 10, sort_by: str = 'quality_score'):
        """
        Récupère les meilleurs prestataires pour une spécialité donnée.
        
        Args:
            specialty: La spécialité recherchée
            top_n: Nombre de prestataires à retourner
            sort_by: Critère de tri ('quality_score', 'waiting_time_days', 'average_cost')
            
        Returns:
            DataFrame avec les prestataires filtrés
        """
        if not self.provider_filter:
            return pd.DataFrame()
        
        return self.provider_filter.filter_by_specialty_name(
            specialty, top_n=top_n, sort_by=sort_by, ascending=(sort_by != 'quality_score')
        )