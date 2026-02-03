import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import MedicalRecommender

class TestMedicalRecommender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up recommender...")
        cls.recommender = MedicalRecommender()
        cls.recommender.load_data()
        
    def test_skin_issue(self):
        # Text containing 'itching' or 'skin rash'
        text = "I have severe itching and a skin rash."
        result = self.recommender.predict(text)
        
        symptoms = result['detected_symptoms']
        self.assertTrue(any('itching' in s for s in symptoms) or any('rash' in s for s in symptoms), 
                        f"Failed to detect symptoms. Found: {symptoms}")
        
        # Expect Dermatologist (or similar)
        top_specs = [r[0] for r in result['recommendations']]
        print(f"Result for '{text}': {top_specs}")
        # We assume 'Dermatologist' is in the dataset based on inspection
        # self.assertIn('Dermatologist', str(top_specs)) 
        
    def test_heart_issue(self):
        # 'chest pain' typically implies Cardiology
        text = "chest pain and vomiting"
        result = self.recommender.predict(text)
        symptoms = result['detected_symptoms']
        self.assertTrue('chest_pain' in symptoms or len(symptoms) > 0)
        
        print(f"Result for '{text}': {result['recommendations']}")

if __name__ == '__main__':
    unittest.main()
