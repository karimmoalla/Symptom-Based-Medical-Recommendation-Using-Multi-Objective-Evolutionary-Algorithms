import re
from typing import List
from deep_translator import GoogleTranslator
from fuzzywuzzy import process
from src.preprocessing import normalize_text

class SymptomExtractor:
    def __init__(self, symptoms_list: List[str]):
        self.symptoms = symptoms_list
        # Nettoyage des noms de colonnes : 'skin_rash' -> 'skin rash'
        self.clean_map = {s.replace('_', ' ').strip().lower(): s for s in self.symptoms}
        
        # Dictionnaire manuel de synonymes FR/EN pour les cas critiques
        # Cela garantit une précision chirurgicale sur les termes fréquents
        self.manual_synonyms = {
            "estomac": "stomach pain",
            "ventre": "abdominal pain",
            "poitrine": "chest pain",
            "coeur": "chest pain", # Souvent confondu par les patients
            "gratte": "itching",
            "boutons": "skin rash",
            "souffle": "breathlessness",
            "tete": "headache",
            "fatigue": "fatigue",
            "fievre": "high fever"
        }

    def extract(self, text: str) -> List[str]:
        # 1. Normalisation initiale du texte brut
        text_raw = text.lower()
        
        # 2. Traduction automatique (FR -> EN)
        try:
            # On traduit pour matcher la base de données qui est en anglais
            translated_text = GoogleTranslator(source='auto', target='en').translate(text_raw)
        except Exception:
            translated_text = text_raw # Fallback si pas d'internet
            
        normalized_input = normalize_text(translated_text)
        found_symptoms = set()

        # 3. Vérification des synonymes manuels (priorité haute)
        # On regarde dans le texte ORIGINAL (FR)
        for fr_term, en_target in self.manual_synonyms.items():
            if fr_term in text_raw:
                found_symptoms.add(self.clean_map.get(en_target, en_target))

        # 4. Recherche par correspondance exacte dans le texte traduit
        for clean_symptom, original_col in self.clean_map.items():
            # Utilisation de Regex pour éviter les faux positifs (ex: "fat" dans "fatigue")
            pattern = r'\b' + re.escape(clean_symptom) + r'\b'
            if re.search(pattern, normalized_input):
                found_symptoms.add(original_col)

        # 5. Fuzzy Matching (pour les fautes de frappe comme "stomach paine")
        # On découpe l'input traduit en segments
        input_segments = normalized_input.split()
        for segment in input_segments:
            if len(segment) < 4: continue # On ignore les petits mots
            
            # On cherche le symptôme le plus proche
            match, score = process.extractOne(segment, self.clean_map.keys())
            if score > 85: # Seuil de confiance
                found_symptoms.add(self.clean_map[match])

        return list(found_symptoms)