import sys
import os
from src.pipeline import MedicalRecommender

def main():
    print("\n" + "="*50)
    print("=== MEDICAL SPECIALITY RECOMMENDER (PHASE 1 & 2) ===")
    print("="*50)
    
    recommender = MedicalRecommender()
    recommender.load_data()
    
    if not recommender.is_ready:
        print("[ERROR] Erreur : Initialisation échouee.")
        return

    print("\n[INFO] Système pret. Extraction multilingue et filtrage des prestataires actives.\n")

    while True:
        print("\n" + "-"*50)
        text = input("Décrivez vos symptômes (ou 'q' pour quitter) :\n> ")
        
        if text.lower() in ['q', 'quit', 'exit']:
            break
            
        # Demander l'âge pour le diagnostic différentiel (optionnel)
        age_input = input("Âge du patient (optionnel, appuyez sur Entrée) : ")
        age = int(age_input) if age_input.isdigit() else None
        
        # Demander si c'est une urgence
        urgent_input = input("Est-ce une urgence ? (y/n) : ").lower()
        is_urgent = True if urgent_input == 'y' else False

        # Demander le budget maximum (optionnel)
        budget_input = input("Budget maximum en € (optionnel, appuyez sur Entrée) : ")
        try:
            budget = float(budget_input) if budget_input.strip() != '' else None
        except Exception:
            budget = None

        # Demander la localisation (optionnel)
        location = input("Localisation (ville/zone, optionnel) : ").strip() or None

        # Poids par défaut pour la combinaison qualité/coût/proximité
        default_wq, default_wc, default_wp = 0.5, 0.3, 0.2
        result = recommender.predict(
            text,
            age=age,
            urgent=is_urgent,
            budget=budget,
            location=location,
            weight_quality=default_wq,
            weight_cost=default_wc,
            weight_proximity=default_wp,
        )
        
        print("\n" + "="*50)
        print("--- PHASE 1 : ANALYSE DES SYMPTÔMES ---")
        print("="*50)
        if not result['detected_symptoms']:
            print("[ALERT] Aucun symptôme médical reconnu. Essayez d'être plus spécifique.")
        else:
            print(f"[OK] Symptômes détectés : {', '.join(result['detected_symptoms'])}")
            print("\n--- SPÉCIALITÉS RECOMMANDÉES (TOP 3) ---")
            for spec, score in result['recommendations']:
                # On affiche le score sous forme de pourcentage de confiance
                print(f"  * {spec.ljust(25)} : {score}% de pertinence")
        
        # PHASE 2 : Affichage des prestataires
        print("\n" + "="*50)
        print("--- PHASE 2 : PRESTATAIRES RECOMMANDÉS ---")
        print("="*50)
        
        if result.get('providers'):
            for specialty, providers_df in result['providers'].items():
                if not providers_df.empty:
                    print(f"\n[CENTRE] {specialty}")
                    print(f"   ({len(providers_df)} prestataires disponibles)")
                    print("   " + "-"*70)
                    
                    # Afficher les 3 meilleurs prestataires
                    for idx, (_, provider) in enumerate(providers_df.head(3).iterrows(), 1):
                        print(f"   {idx}. {provider['provider_name']}")
                        print(f"      [QUALITE] Qualité: {provider['quality_score']}/5 | "
                              f"[ATTENTE] Attente: {provider['waiting_time_days']} jours | "
                              f"[COUT] Coût: {provider['average_cost']}€")
                        print()
                else:
                    print(f"\n[ALERT] {specialty}: Aucun prestataire trouvé")
        else:
            print("\n[ALERT] Aucun prestataire disponible pour les spécialités recommandées.")
        
        print("-"*50)

if __name__ == "__main__":
    main()