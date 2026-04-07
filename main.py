import sys
import os
import argparse
from src.pipeline import MedicalRecommender

def main():
    parser = argparse.ArgumentParser(description="Système de Recommandation Médicale (Phases 1 & 2)")
    parser.add_argument("text", nargs="?", default=None, help="Description des symptômes du patient")
    parser.add_argument("--age", type=int, default=None, help="Âge du patient (optionnel)")
    parser.add_argument("--urgent", action="store_true", help="Cochez ce flag si c'est une urgence")
    parser.add_argument("--budget", type=float, default=None, help="Budget maximum en euros (optionnel)")
    parser.add_argument("--location", type=str, default=None, help="Ville ou zone géographique (optionnel)")
    parser.add_argument("--interactive", action="store_true", help="Lancer en mode interactif")

    args = parser.parse_args()

    print("\n" + "="*50)
    print("=== MEDICAL SPECIALITY RECOMMENDER ===")
    print("="*50)
    
    recommender = MedicalRecommender()
    recommender.load_data()
    
    if not recommender.is_ready:
        print("[ERROR] Erreur : Initialisation échouée.")
        sys.exit(1)

    if args.interactive:
        run_interactive_mode(recommender)
    else:
        text = args.text
        if text is None:
            text = input("Décrivez vos symptômes :\n> ")
            if not text.strip():
                sys.exit(0)
        
        run_prediction(recommender, text, args.age, args.urgent, args.budget, args.location)

def run_prediction(recommender, text, age, is_urgent, budget, location):
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
        return
    
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
        best_doc = nsga_top.iloc[0]
        
        p_name = best_doc.get('provider_name', 'Médecin Inconnu')
        p_spec = best_doc.get('specialty', 'N/A')
        p_qual = best_doc.get('quality_score', 0)
        
        p_cost = best_doc.get('average_cost')
        if p_cost is None or str(p_cost) == 'nan':
                p_cost = best_doc.get('consultation_cost', 0)
        
        p_wait = best_doc.get('waiting_time_days', 0)
        
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

        if len(nsga_top) > 1:
            print("\n   ALTERNATIVES (Top 2 & 3) :")
            rank = 2
            for idx, row in nsga_top.iloc[1:].iterrows():
                alt_name = row.get('provider_name')
                alt_cost = row.get('average_cost') if str(row.get('average_cost')) != 'nan' else row.get('consultation_cost', 0)
                print(f"   #{rank}. {alt_name} (Coût: {alt_cost}€, Qualité: {row.get('quality_score')}/5)")
                rank += 1
    else:
        print("[INFO] Aucun médecin optimisé trouvé pour la meilleure spécialité.")
        print("(Essayez d'élargir vos critères ou de vérifier l'orthographe de la localisation)")
        
    print("-" * 60)

def run_interactive_mode(recommender):
    print("\n[INFO] Système prêt. Mode interactif (Optimisation NSGA-II).\n")

    while True:
        print("\n" + "-"*50)
        text = input("Décrivez vos symptômes (ou 'q' pour quitter) :\n> ")
        
        if text.lower() in ['q', 'quit', 'exit']:
            break
            
        age_input = input("Âge du patient (optionnel, appuyez sur Entrée) : ")
        age = int(age_input) if age_input.isdigit() else None
        
        urgent_input = input("Est-ce une urgence ? (y/n) : ").lower()
        is_urgent = True if urgent_input == 'y' else False

        budget_input = input("Budget maximum en € (focus sur prix le plus proche) [optionnel] : ")
        try:
            budget = float(budget_input) if budget_input.strip() != '' else None
        except Exception:
            budget = None

        location = input("Localisation (ville/zone) [optionnel] : ").strip() or None

        run_prediction(recommender, text, age, is_urgent, budget, location)

if __name__ == "__main__":
    main()