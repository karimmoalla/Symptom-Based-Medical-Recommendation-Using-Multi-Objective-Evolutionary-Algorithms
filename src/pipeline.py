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
        """
        Load data and initialize components.
        """
        print(f"Loading data from {DATA_FILE}...")
        try:
            self.df = pd.read_excel(DATA_FILE)
            # CLEAN DATA: Strip whitespace from column names
            self.df.columns = self.df.columns.str.strip()
            print(f"Data loaded: {self.df.shape}")
            
            # Initialize Extractor
            # features are all columns except target and metadata
            symptom_cols = [c for c in self.df.columns if c != TARGET_COL and 'Unnamed' not in c]
            self.extractor = SymptomExtractor(symptom_cols)
            
            # Initialize Scorer
            self.scorer = SpecialtyScorer(self.df)
            
            self.is_ready = True
            print("System initialized successfully.")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.is_ready = False

    def predict(self, text: str, top_n: int = 3):
        if not self.is_ready:
            return {"error": "System not initialized. Call load_data() first."}

        # 1. Pipeline: Text -> Symptoms
        detected_symptoms = self.extractor.extract(text)
        
        # 2. Pipeline: Symptoms -> Scores
        scores = self.scorer.score(detected_symptoms)
        
        # 3. Pipeline: Formatting
        top_results = self.scorer.get_top_n(scores, top_n)
        
        return {
            "input_text": text,
            "detected_symptoms": detected_symptoms,
            "recommendations": top_results
            # "debug_scores": scores
        }
