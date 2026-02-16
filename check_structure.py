import pandas as pd

print("=== Specialist.xlsx ===")
df_specialist = pd.read_excel('Specialist.xlsx')
print(f"Colonnes: {df_specialist.columns.tolist()}")
print(f"Shape: {df_specialist.shape}")
print(f"Spécialités (Disease) - premières 10:")
specs = df_specialist['Disease'].unique()[:10]
for s in specs:
    print(f"  - {s}")

print("\n=== Medical_Providers_Aligned_With_Specialties.xlsx ===")
df_providers = pd.read_excel('Medical_Providers_Aligned_With_Specialties.xlsx')
print(f"Colonnes: {df_providers.columns.tolist()}")
print(f"Shape: {df_providers.shape}")
print(f"Type de la colonne 'specialty': {df_providers['specialty'].dtype}")
print(f"Quelques valeurs de specialty: {df_providers['specialty'].head(15).tolist()}")
