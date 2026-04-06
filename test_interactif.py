from src.pipeline import MedicalRecommender

def main():
    print("======================================================")
    print("   TEST INTERACTIF - SYSTEME DE RECOMMANDATION MEDICAL")
    print("======================================================")
    
    # Initialisation du système
    recommender = MedicalRecommender()
    recommender.load_data()
    
    print("\n[Système prêt ! Entrez 'q' ou 'quitter' pour arrêter.]\n")
    
    while True:
        # Saisie des symptômes par l'utilisateur
        text = input("Quels sont vos symptômes ?\n> ")
        
        if text.lower() in ['q', 'quitter', 'exit']:
            print("Fin du test. Au revoir !")
            break
            
        if not text.strip():
            continue
            
        # Saisie d'informations complémentaires (optionnel)
        budget_input = input("Budget maximum (TND) ? (Laissez vide si peu importe): ")
        budget = float(budget_input) if budget_input.strip() else None
        
        local_input = input("Quelle est votre ville ? (Ex: Tunis, Sousse, Sfax... ou vide) : ")
        location = local_input.strip() if local_input.strip() else None
        
        print("\n--- ANALYSE EN COURS ... ---")
        
        # Lancement de la prédiction K1 + K2 + NSGA-II
        res = recommender.predict(
            text=text,
            budget=budget,
            location=location
        )
        
        print("\n=== 1. SYMPTÔMES COMPRIS PAR L'IA (K1) ===")
        if res.get('detected_symptoms'):
            print(f"-> {', '.join(res.get('detected_symptoms'))}")
        else:
            print("-> Aucun symptôme formel reconnu (Essayez de reformuler).")
            continue
            
        print("\n=== 2. SPÉCIALITÉS RECOMMANDÉES (K1) ===")
        for i, (spec, score) in enumerate(res.get('recommendations', [])[:3], 1):
            print(f"{i}. {spec} (Confiance : {score}%)")
            
        print("\n=== 3. MEILLEURS MÉDECINS (K2 + Optimisation NSGA-II) ===")
        # On affiche juste l'optimisation NSGA-II de la meilleure spécialité
        nsga_top = res.get('top_specialty_providers')
        
        if nsga_top is not None and not nsga_top.empty:
            print(f"\nPour consulter un(e) {res['recommendations'][0][0]}, voici les médecins optimisés :")
            
            # On formate l'affichage des médecins
            display_cols = ['provider_name', 'location', 'quality_score', 'average_cost', 'waiting_time_days', 'available_slots']
            existing_cols = [c for c in display_cols if c in nsga_top.columns]
            
            # Renommer pour l'affichage console propre
            renames = {
                'provider_name': 'Médecin',
                'location': 'Ville',
                'quality_score': 'Qualité (/10)',
                'average_cost': 'Prx (TND)',
                'waiting_time_days': 'Délai (j)',
                'available_slots': 'Créneaux'
            }
            
            print(nsga_top[existing_cols].rename(columns=renames).to_string(index=False))
        else:
            print("-> Aucun médecin trouvé correspondant à vos critères optimisés.")
            
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()
