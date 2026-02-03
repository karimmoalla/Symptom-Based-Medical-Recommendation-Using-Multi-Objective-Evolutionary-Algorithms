import sys
import os
from src.pipeline import MedicalRecommender

def main():
    print("\n" + "="*50)
    print("=== MEDICAL SPECIALITY RECOMMENDER (PHASE 1) ===")
    print("="*50)
    
    recommender = MedicalRecommender()
    recommender.load_data()
    
    if not recommender.is_ready:
        print("Erreur : Initialisation échouée.")
        return

    print("\n[INFO] Système prêt. Extraction multilingue et gestion de négation activées.")
    
    while True:
        print("\n" + "-"*30)
        text = input("Décrivez vos symptômes (ou 'q' pour quitter) :\n> ")
        
        if text.lower() in ['q', 'quit', 'exit']:
            break
            
        # Demander l'âge pour le diagnostic différentiel (optionnel)
        age_input = input("Âge du patient (optionnel, appuyez sur Entrée) : ")
        age = int(age_input) if age_input.isdigit() else None
        
        # Demander si c'est une urgence
        urgent_input = input("Est-ce une urgence ? (y/n) : ").lower()
        is_urgent = True if urgent_input == 'y' else False

        # Lancement de la prédiction "Zéro Limite"
        result = recommender.predict(text, age=age, urgent=is_urgent)
        
        print("\n--- ANALYSE ---")
        if not result['detected_symptoms']:
            print("⚠️ Aucun symptôme médical reconnu. Essayez d'être plus spécifique.")
        else:
            print(f"✅ Symptômes détectés : {', '.join(result['detected_symptoms'])}")
            print("\n--- RECOMMANDATIONS (TOP 3) ---")
            for spec, score in result['recommendations']:
                # On affiche le score sous forme de pourcentage de confiance
                print(f"📍 {spec.ljust(20)} : {score}% de pertinence")
        
        print("-"*30)

if __name__ == "__main__":
    main()