import pandas as pd
import hashlib
from collections import defaultdict

# Charger les deux fichiers
df_specialist = pd.read_excel('Specialist.xlsx')
df_providers = pd.read_excel('Medical_Providers_Aligned_With_Specialties.xlsx')

print("="*60)
print("CRÉATION DE LA CORRESPONDANCE SPÉCIALITÉS")
print("="*60)

# Récupérer les spécialités uniques du fichier Specialist
specialties = df_specialist['Disease'].unique()
print(f"\n✓ Spécialités trouvées dans Specialist.xlsx : {len(specialties)}")
for i, spec in enumerate(sorted(specialties)[:15]):
    print(f"  {i+1}. {spec}")

# IDs uniques dans Medical_Providers
provider_specialty_ids = sorted(df_providers['specialty'].unique())
print(f"\n✓ IDs de spécialités uniques dans Medical_Providers : {len(provider_specialty_ids)}")
print(f"  Premiers IDs : {provider_specialty_ids[:20]}")

# Créer une correspondance : hasher chaque spécialité
print("\n" + "="*60)
print("MAPPING SPÉCIALITÉS → IDS")
print("="*60)

mapping_name_to_id = {}
mapping_id_to_name = {}

# Créer une correspondance basée sur un hash des spécialités
for idx, specialty in enumerate(sorted(specialties)):
    # Créer un ID numérique basé sur le hash
    hash_value = int(hashlib.md5(specialty.encode()).hexdigest(), 16) % (10000)
    mapping_name_to_id[specialty] = hash_value
    mapping_id_to_name[hash_value] = specialty
    print(f"{specialty:30} → ID: {hash_value}")

print("\n" + "="*60)
print("ANALYSE DES CORRESPONDANCES POSSIBLES")
print("="*60)

# Vérifier combien de spécialités correspondent
matched_count = 0
for provider_id in provider_specialty_ids[:50]:  # Vérifier les 50 premiers
    if provider_id in mapping_id_to_name:
        matched_count += 1
        print(f"✓ ID {provider_id} correspond à {mapping_id_to_name[provider_id]}")
    else:
        # Chercher la spécialité la plus proche
        specialty_name = f"Unknown_{provider_id}"
        print(f"  ID {provider_id} - pas de correspondance trouvée (assigned to: {specialty_name})")

print(f"\nCorrespondances trouvées : {matched_count}/{len(provider_specialty_ids[:50])}")

# Sauvegarder le mapping
print("\n" + "="*60)
print("OPTION : Vous pouvez créer une correspondance manuelle")
print("="*60)
print("\nVérifiez les IDs de spécialités dans la base de données des prestataires")
print("et créez une correspondance dans config.py ou un fichier séparé")
