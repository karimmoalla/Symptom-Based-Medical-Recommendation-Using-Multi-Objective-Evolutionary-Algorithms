import re
from typing import List, Set
from deep_translator import GoogleTranslator
from fuzzywuzzy import process, fuzz

class SymptomExtractor:
    def __init__(self, symptoms_list: List[str]):
        # On nettoie TOUT : on enlève les espaces et on met en minuscule
        # ' skin_rash ' -> 'skin_rash'
        self.symptoms = [str(s).strip() for s in symptoms_list]
        
        # Dictionnaire de secours (Mapping direct)
        self.manual_keywords = {
            "dizzy": "dizziness",
            "vertigo": "dizziness",
            "head": "headache",
            "stomach": "stomach_pain",
            "skin": "skin_rash",
            "itch": "itching",
            "vomit": "vomiting",
            "fever": "high_fever"
        }

    def extract(self, text: str) -> List[str]:
        # 1. Traduction
        try:
            text_en = GoogleTranslator(source='auto', target='en').translate(text).lower()
            print(f"[DEBUG] Traduction : {text_en}")
        except:
            text_en = text.lower()

        found_symptoms = set()

        # 2. Vérification par mots-clés manuels
        for key, target_val in self.manual_keywords.items():
            if key in text_en:
                # On cherche la colonne qui contient ce mot-clé dans l'Excel
                for col_name in self.symptoms:
                    if target_val.lower() in col_name.lower():
                        found_symptoms.add(col_name)

        # 3. Vérification par correspondance dans les noms de colonnes
        # On regarde si un nom de symptôme est contenu dans la phrase
        for col_name in self.symptoms:
            # On transforme 'skin_rash' en 'skin rash' pour comparer
            readable_name = col_name.replace('_', ' ').lower()
            if readable_name in text_en and len(readable_name) > 3:
                found_symptoms.add(col_name)

        # 4. Fuzzy Matching (si rien n'est trouvé)
        if not found_symptoms:
            # On compare la phrase entière aux colonnes
            match, score = process.extractOne(text_en, self.symptoms, scorer=fuzz.partial_ratio)
            if score > 80:
                found_symptoms.add(match)

        return list(found_symptoms)