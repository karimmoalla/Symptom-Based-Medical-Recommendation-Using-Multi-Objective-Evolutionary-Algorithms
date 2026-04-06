#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Examples of using the Phase 2 Provider Filtering System
Démonstration du système de filtrage des prestataires (Phase 2)
"""

from src.pipeline import MedicalRecommender
import pandas as pd

def example_1_basic_prediction():
    """
    Example 1: Basic prediction with symptoms and provider filtering
    Exemple 1 : Prédiction simple avec symptômes et filtrage
    """
    print("\n" + "="*70)
    print("EXEMPLE 1 : Prédiction simple avec symptômes")
    print("="*70)
    
    recommender = MedicalRecommender()
    recommender.load_data()
    
    # Patient context: budget and location
    budget = 80.0  # euros
    location = 'Paris'

    # Weights pour la combinaison qualité/coût/proximité (doivent idéalement sommer à 1)
    wq, wc, wp = 0.5, 0.3, 0.2

    # Predict (inclut budget, localisation et poids)
    result = recommender.predict(
        text="Très forte tête et vomissements",
        age=28,
        urgent=False,
        budget=budget,
        location=location,
        weight_quality=wq,
        weight_cost=wc,
        weight_proximity=wp
    )
    
    # Display results
    print(f"\nSymptômes détectés: {result['detected_symptoms']}")
    print(f"Contexte patient: budget={budget}€, location={location}, weights=(q={wq},c={wc},p={wp})")
    print(f"\nSpécialités recommandées:")
    for spec, score in result['recommendations']:
        print(f"  - {spec}: {score}%")
    
    print(f"\nPrestataires trouvés:")
    for specialty, providers_df in result['providers'].items():
        print(f"\n  {specialty}: {len(providers_df)} providers")
        for idx, (_, prov) in enumerate(providers_df.head(2).iterrows(), 1):
            print(f"    {idx}. {prov['provider_name']} - Quality: {prov['quality_score']}")


def example_2_get_by_specialty():
    """
    Example 2: Get providers for a specific specialty
    Exemple 2 : Obtenir les prestataires d'une spécialité spécifique
    """
    print("\n" + "="*70)
    print("EXEMPLE 2 : Obtenir les prestataires d'une spécialité")
    print("="*70)
    
    recommender = MedicalRecommender()
    recommender.load_data()
    
    # Get cardiologists
    cardiologists = recommender.get_providers_for_specialty(
        specialty='Cardiologist',
        top_n=5,
        sort_by='quality_score'
    )
    
    print(f"\nTop 5 Cardiologists (triés par qualité):")
    if not cardiologists.empty:
        for idx, (_, prov) in enumerate(cardiologists.iterrows(), 1):
            print(f"  {idx}. {prov['provider_name']:30} | "
                  f"Quality: {prov['quality_score']:.2f} | "
                  f"Cost: {prov['average_cost']:.0f}€ | "
                  f"Wait: {prov['waiting_time_days']} days")
    else:
        print("  No providers found")


def example_3_sort_by_cost():
    """
    Example 3: Get providers sorted by cost (cheapest first)
    Exemple 3 : Obtenir les prestataires les moins chers
    """
    print("\n" + "="*70)
    print("EXEMPLE 3 : Prestataires les moins chers")
    print("="*70)
    
    recommender = MedicalRecommender()
    recommender.load_data()
    
    # Get providers sorted by cost (ascending)
    result = recommender.predict(
        text="persistent cough and fever",
        age=None,
        urgent=False
    )
    
    # Access the filter directly for sorting by cost
    if result['recommendations']:
        specialty = result['recommendations'][0][0]  # First specialty
        providers = recommender.get_providers_for_specialty(
            specialty=specialty,
            top_n=5,
            sort_by='average_cost'
        )
        
        print(f"\nTop 5 {specialty} providers (triés par coût):")
        for idx, (_, prov) in enumerate(providers.iterrows(), 1):
            print(f"  {idx}. {prov['provider_name']:30} | "
                  f"Cost: {prov['average_cost']:.0f}€ | "
                  f"Quality: {prov['quality_score']:.2f} | "
                  f"Wait: {prov['waiting_time_days']} days")


def example_4_emergency():
    """
    Example 4: Emergency case
    Exemple 4 : Cas d'urgence
    """
    print("\n" + "="*70)
    print("EXEMPLE 4 : Cas d'urgence")
    print("="*70)
    
    recommender = MedicalRecommender()
    recommender.load_data()
    
    # Emergency prediction
    result = recommender.predict(
        text="Severe chest pain and difficulty breathing",
        age=55,
        urgent=True  # Mark as urgent
    )
    
    print(f"\n[URGENCE] URGENCE DÉTECTÉE")
    print(f"\nSymptômes: {result['detected_symptoms']}")
    print(f"Spécialités recommandées (urgence):")
    for spec, score in result['recommendations']:
        print(f"  - {spec}: {score}%")
    
    # For emergencies, sort by shortest waiting time
    if result['recommendations']:
        specialty = result['recommendations'][0][0]
        providers = recommender.get_providers_for_specialty(
            specialty=specialty,
            top_n=5,
            sort_by='waiting_time_days'
        )
        
        print(f"\n{specialty} (prestataires avec délais les plus courts):")
        for idx, (_, prov) in enumerate(providers.iterrows(), 1):
            print(f"  {idx}. {prov['provider_name']:30} | "
                  f"Wait: {prov['waiting_time_days']} days | "
                  f"Quality: {prov['quality_score']:.2f}")


def example_5_statistics():
    """
    Example 5: Get statistics for a specialty
    Exemple 5 : Obtenir les statistiques pour une spécialité
    """
    print("\n" + "="*70)
    print("EXEMPLE 5 : Statistiques par spécialité")
    print("="*70)
    
    recommender = MedicalRecommender()
    recommender.load_data()
    
    # Get provider filter to access statistics
    stats = recommender.provider_filter.get_statistics('Dermatologist')
    
    if stats:
        print(f"\nDermatologist Statistics:")
        print(f"  Number of providers: {stats['count']}")
        print(f"  Average quality score: {stats['avg_quality_score']:.2f}/5")
        print(f"  Average cost: {stats['avg_cost']:.0f}€")
        print(f"  Average waiting time: {stats['avg_waiting_time']:.1f} days")
        print(f"  Cost range: {stats['min_cost']:.0f}€ - {stats['max_cost']:.0f}€")


if __name__ == "__main__":
    print("This file contains example functions. To use the interactive CLI, run: python main.py")
    print("If you want to run a specific example, import the function and call it from Python:")
    print("  from examples import example_1_basic_prediction; example_1_basic_prediction()")
