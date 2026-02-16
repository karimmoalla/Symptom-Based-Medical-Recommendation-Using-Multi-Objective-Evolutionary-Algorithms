#!/usr/bin/env python
from src.pipeline import MedicalRecommender

r = MedicalRecommender()
r.load_data()

text = (
    "Depuis 5 jours : céphalées très violentes en casque, nausées et vomissements intermittents, "
    "    python run_demo.py "
    "A pris ibuprofène sans amélioration. Douleur augmentée à l'effort. Voyage récent en Espagne."
)

res = r.predict(
    text=text,
    age=46,
    urgent=True,
    budget=80,
    location="Paris"
)

print("\n=== DEMO INPUT ===")
print(text)
print("\n=== DETECTED SYMPTOMS ===")
print(res.get('detected_symptoms'))
print("\n=== RECOMMENDATIONS ===")
print(res.get('recommendations'))
print("\n=== PROVIDERS (top by specialty using standard weights) ===")
for spec, df in res.get('providers', {}).items():
    print(f"\n{spec} ({len(df)} providers)")
    cols = [c for c in ['provider_name','quality_score','average_cost','waiting_time_days'] if c in df.columns]
    print(df[cols].head(5).to_string(index=False))

print("\n=== OPTIMIZED PROVIDERS (Best for top specialty via NSGA-II) ===")
nsga_top = res.get('top_specialty_providers')
if nsga_top is not None and not nsga_top.empty:
    cols = [c for c in ['provider_name','quality_score','average_cost','waiting_time_days'] if c in nsga_top.columns]
    print(nsga_top[cols].to_string(index=False))
else:
    print("No optimized providers found.")
