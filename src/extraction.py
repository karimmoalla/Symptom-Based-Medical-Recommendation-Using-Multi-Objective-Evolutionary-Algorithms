import re
from typing import List, Set
from deep_translator import GoogleTranslator
from fuzzywuzzy import process, fuzz

class SymptomExtractor:
    def __init__(self, symptoms_list: List[str]):
        # La liste officielle du modèle (ex: "yellowing_of_eyes")
        self.symptoms = [str(s).strip() for s in symptoms_list]
        
        # Version lisible "yellowing_of_eyes" -> "yellowing of eyes"
        self.readable_symptoms = {s: s.replace('_', ' ').lower() for s in self.symptoms}

        # Dictionnaire de synonymes cliniques pour capter le langage naturel
        self.synonyms = {
            "dizzy": "dizziness",
            "vertigo": "dizziness",
            "head ache": "headache",
            "head aches": "headache",
            "migraine": "headache",
            "tummy ache": "abdominal_pain",
            "stomach ache": "abdominal_pain",
            "stomach pain": "abdominal_pain",
            "belly pain": "abdominal_pain",
            "throw up": "vomiting",
            "throwing up": "vomiting",
            "puke": "vomiting",
            "puking": "vomiting",
            "sick to stomach": "nausea",
            "fever": "high_fever",
            "temperature": "high_fever",
            "hot": "high_fever",
            "yellow eyes": "yellowing_of_eyes",
            "eyes turning yellow": "yellowing_of_eyes",
            "yellow of eyes": "yellowing_of_eyes",
            "yellow skin": "yellowish_skin",
            "skin turning yellow": "yellowish_skin",
            "itchy": "itching",
            "itchiness": "itching",
            "scratching": "itching",
            "tired": "fatigue",
            "tiredness": "fatigue",
            "exhausted": "fatigue",
            "exhaustion": "fatigue",
            "weak": "fatigue",
            "loss of smell": "loss_of_smell",
            "can't smell": "loss_of_smell",
            "no smell": "loss_of_smell",
            "hair loss": "alopecia",
            "losing hair": "alopecia",
            "can't breathe": "breathlessness",
            "short of breath": "breathlessness",
            "hard to breathe": "breathlessness",
            "heart beating fast": "palpitations",
            "heart racing": "palpitations",
            "chest pain": "chest_pain",
            "chest hurt": "chest_pain",
            "chest tight": "chest_tightness",
            "heavy chest": "chest_tightness",
            "runny nose": "continuous_sneezing",
            "sneezing": "continuous_sneezing",
            "sore throat": "throat_irritation",
            "throat hurt": "throat_irritation",
            "cough": "cough",
            "coughing": "cough",
            "blood in urine": "hematuria",
            "peeing blood": "hematuria",
            "peeing a lot": "polyuria",
            "frequent urination": "polyuria",
            "red eye": "eye_redness",
            "red eyes": "eye_redness",
            "bloodshot eyes": "eye_redness",
            "vision": "visual_disturbances",
            "double vision": "diplopia",
            "black stool": "black_stools",
            "dark stool": "black_stools",
            "tarry stool": "black_stools",
            "blood in stool": "bloody_stool",
            "pooping blood": "bloody_stool",
            "swollen stomach": "swelling_of_stomach",
            "bloated": "swelling_of_stomach",
            "bloating": "swelling_of_stomach",
            "diarrhea": "diarrhoea",
            "watery stool": "diarrhoea",
            "constipated": "constipation",
            "can't poop": "constipation",
            "muscle pain": "muscle_pain",
            "muscle hurt": "muscle_pain",
            "joint pain": "joint_pain",
            "knee pain": "joint_pain",
            "back pain": "back_pain",
            "back hurt": "back_pain",
            "neck pain": "neck_pain",
            "weight loss": "weight_loss",
            "losing weight": "weight_loss",
            "weight gain": "weight_gain",
            "gaining weight": "weight_gain",
            "sweat": "sweating",
            "sweating": "sweating"
        }

    def _generate_ngrams(self, text: str, n_max: int = 4) -> List[str]:
        words = re.findall(r'\b\w+\b', text)
        ngrams = []
        for n in range(1, n_max + 1):
            for i in range(len(words) - n + 1):
                ngrams.append(" ".join(words[i:i+n]))
        return ngrams

    def extract(self, text: str) -> List[str]:
        # 1. Traduction du texte utilisateur vers l'anglais
        try:
            text_en = GoogleTranslator(source='auto', target='en').translate(text).lower()
            print(f"[DEBUG] Traduction : {text_en}")
        except Exception as e:
            text_en = text.lower()
            print(f"[DEBUG] Erreur traduction : {e}")

        found_symptoms = set()

        # 2. Chercher des synonymes connus dans le texte
        # Plus permissif : on regarde simplement si la sous-chaine est dans le texte
        for synonym, target_symptom in self.synonyms.items():
            # Remplacement des expressions complexes
            if synonym in text_en:
                if target_symptom in self.symptoms:
                    found_symptoms.add(target_symptom)
            
            # Gestion basique des pluriels (ex: black stools)
            elif synonym + 's' in text_en:
                if target_symptom in self.symptoms:
                    found_symptoms.add(target_symptom)

        # 3. Correspondance exacte sur les noms de symptômes lisibles
        for sym_id, readable_name in self.readable_symptoms.items():
            if re.search(r'\b' + re.escape(readable_name) + r'\b', text_en):
                found_symptoms.add(sym_id)

        # 4. Fuzzy Matching optimisé via N-Grams
        # C'est la garantie qu'on ne rate pas un symptôme écrit avec une petite faute
        ngrams = self._generate_ngrams(text_en, n_max=3)
        rev_readable = {v: k for k, v in self.readable_symptoms.items()}
        
        for ngram in ngrams:
            # Éviter de faire du fuzzy sur des mots trop courts de moins de 4 lettres
            if len(ngram) < 4:
                continue
                
            match, score = process.extractOne(ngram, list(rev_readable.keys()), scorer=fuzz.ratio)
            if score >= 85: # Seuil strict
                found_symptoms.add(rev_readable[match])

        # 5. Dernier filet de sécurité : Fallback global (token_set_ratio)
        # Très puissant pour rattraper "eyes turning yellow" -> "yellowing of eyes"
        for sym_id, readable_name in self.readable_symptoms.items():
            if sym_id not in found_symptoms:
                score = fuzz.token_set_ratio(text_en, readable_name)
                # Si le score de chevauchement sémantique est très élevé
                if score >= 90:  # 90 car token_set_ratio est très permissif
                    found_symptoms.add(sym_id)

        print(f"[DEBUG] Symptômes finaux envoyés au K1 Brain : {list(found_symptoms)}")
        return list(found_symptoms)
