#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test script for the PCD-Recommandation system

from src.pipeline import MedicalRecommender

print("Testing Medical Recommender System...")
print("-" * 60)

try:
    # Initialize
    print("1. Initializing system...")
    recommender = MedicalRecommender()
    recommender.load_data()
    print("   ✓ System initialized")
    
    if not recommender.is_ready:
        print("   ✗ System not ready!")
        exit(1)
    
    # Test prediction
    print("\n2. Testing prediction with sample symptoms...")
    result = recommender.predict("headache and dizziness")
    print(f"   ✓ Prediction completed")
    print(f"   - Detected symptoms: {result.get('detected_symptoms')}")
    print(f"   - Recommendations: {[spec for spec, _ in result.get('recommendations', [])]}")
    print(f"   - Providers found: {len(result.get('providers', {}))}")
    
    # Show providers by specialty
    if result.get('providers'):
        print("\n3. Providers by specialty:")
        for specialty, providers_df in result['providers'].items():
            print(f"   - {specialty}: {len(providers_df)} providers")
    else:
        print("\n3. ⚠️  No providers found for the specialties")
    
    print("\n" + "-" * 60)
    print("✓ Test completed successfully!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
