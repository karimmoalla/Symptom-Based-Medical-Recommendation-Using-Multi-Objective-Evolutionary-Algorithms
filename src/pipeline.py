import pandas as pd
from src.config import DATA_FILE, TARGET_COL
from src.preprocessing import normalize_text
from src.extraction import SymptomExtractor
from src.scoring import SpecialtyScorer

class MedicalRecommender:
    def __init__(self):
        self.df = None
        self.extractor = None
        self.scorer = None
        self.is_ready = False

    def load_data(self):
        print(f"Loading data from {DATA_FILE}...")
        try:
            self.df = pd.read_excel(DATA_FILE)
            self.df.columns = self.df.columns.str.strip()
            
            symptom_cols = [c for c in self.df.columns if c != TARGET_COL and 'Unnamed' not in c]
            self.extractor = SymptomExtractor(symptom_cols)
            self.scorer = SpecialtyScorer(self.df)
            
            self.is_ready = True
            print("System initialized successfully.")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.is_ready = False

    def predict(self, text: str, age: int = None, urgent: bool = False, top_n: int = 3):
        if not self.is_ready:
            return {"error": "System not initialized."}

        # 1. Extraction intelligente (gère la négation et la langue)
        detected_symptoms = self.extractor.extract(text)
        
        # 2. Scoring avancé (gère la spécificité et le profil patient)
        # On passe l'âge et l'urgence au scorer
        scores = self.scorer.score(detected_symptoms, patient_age=age, is_urgent=urgent)
        
        # 3. Formatage des résultats
        top_results = self.scorer.get_top_n(scores, top_n)
        
        return {
            "input_text": text,
            "detected_symptoms": detected_symptoms,
            "recommendations": top_results,
            "patient_context": {"age": age, "urgent": urgent}
        }