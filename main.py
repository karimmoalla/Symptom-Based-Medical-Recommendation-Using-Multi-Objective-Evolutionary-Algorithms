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

    print("\n[INFO] Système pret. Mode interactif (Optimisation NSGA-II).\n")

    while True:
        print("\n" + "-"*50)
        text = input("Décrivez vos symptômes (ou 'q' pour quitter) :\n> ")
        
        if text.lower() in ['q', 'quit', 'exit']:
            break
            
        # Saisie de l'âge
        age_input = input("Âge du patient (optionnel, appuyez sur Entrée) : ")
        age = int(age_input) if age_input.isdigit() else None
        
        # Saisie urgence
        urgent_input = input("Est-ce une urgence ? (y/n) : ").lower()
        is_urgent = True if urgent_input == 'y' else False

        # Saisie budget
        budget_input = input("Budget maximum en € (focus sur prix le plus proche) [optionnel] : ")
        try:
            budget = float(budget_input) if budget_input.strip() != '' else None
        except Exception:
            budget = None

        # Saisie localisation
        location = input("Localisation (ville/zone) [optionnel] : ").strip() or None

        # Appel au moteur de recommandation
        try:
            result = recommender.predict(
                text,
                age=age,
                urgent=is_urgent,
                budget=budget,
                location=location
            )
        except Exception as e:
            print(f"[ERROR] Une erreur est survenue lors de la prédiction : {e}")
            continue
        
        print("\n" + "="*60)
        print("          RÉSULTATS DE L'ANALYSE")
        print("="*60)

        # 1. Symptômes
        if not result['detected_symptoms']:
             print("[ALERT] Aucun symptôme détecté. Essayez d'être plus précis.")
        else:
             print(f"[SYMPTÔMES] Détectés : {', '.join(result['detected_symptoms'])}")

        # 2. Recommandations de Spécialités
        print("\n[DIAGNOSTIC] Spécialités médicales conseillées (par ordre de pertinence) :")
        if result['recommendations']:
            for i, (spec, score) in enumerate(result['recommendations'], 1):
                print(f"  {i}. {spec} (Confiance : {score:.1f}%)")
        else:
            print("  Aucune spécialité trouvée.")

        # 3. Médecins Optimisés (NSGA-II)
        print("\n" + "="*60)
        print("   TOP MÉDECIN RECOMMANDÉ (Choix Optimal Multicritères)")
        print("="*60)
        
        nsga_top = result.get('top_specialty_providers')
        
        if nsga_top is not None and not nsga_top.empty:
            # Récupérer le meilleur candidat (le premier de la liste triée par NSGA-II)
            best_doc = nsga_top.iloc[0]
            
            p_name = best_doc.get('provider_name', 'Médecin Inconnu')
            p_spec = best_doc.get('specialty', 'N/A')
            p_qual = best_doc.get('quality_score', 0)
            
            # Gestion des différentes colonnes de prix possibles
            p_cost = best_doc.get('average_cost')
            if p_cost is None or str(p_cost) == 'nan':
                    p_cost = best_doc.get('consultation_cost', 0)
            
            p_wait = best_doc.get('waiting_time_days', 0)
            
            # Gestion localisation / adresse
            p_loc  = best_doc.get('city')
            if not p_loc or str(p_loc) == 'nan':
                p_loc = best_doc.get('location')
            if not p_loc or str(p_loc) == 'nan':
                    p_loc = best_doc.get('address', 'N/A')
            
            print(f"\n   MEILLEUR CHOIX : {p_name}")
            print(f"   Spécialité : {p_spec}")
            print(f"   ------------------------------------------------")
            print(f"   - Qualité   : {p_qual}/5")
            print(f"   - Coût      : {p_cost} €")
            print(f"   - Attente   : {p_wait} jours")
            print(f"   - Lieu      : {p_loc}")
            print(f"   ------------------------------------------------")

            # Afficher les alternatives si disponibles
            if len(nsga_top) > 1:
                print("\n   ALTERNATIVES (Top 2 & 3) :")
                rank = 2
                for idx, row in nsga_top.iloc[1:].iterrows():
                    alt_name = row.get('provider_name')
                    alt_cost = row.get('average_cost') or row.get('consultation_cost') or 0
                    print(f"   #{rank}. {alt_name} (Coût: {alt_cost}€, Qualité: {row.get('quality_score')}/5)")
                    rank += 1
        else:
            print("[INFO] Aucun médecin optimisé trouvé pour la meilleure spécialité.")
            print("(Essayez d'élargir vos critères ou de vérifier l'orthographe de la localisation)")
            
        print("-"*60)

if __name__ == "__main__":
    main()