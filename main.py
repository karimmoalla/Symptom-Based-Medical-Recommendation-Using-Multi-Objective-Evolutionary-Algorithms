import sys
import os
# Add src to path if needed, though structure allows running from root
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline import MedicalRecommender

def main():
    print("=== Medical Speciality Recommender (Phase 1) ===")
    
    recommender = MedicalRecommender()
    recommender.load_data()
    
    if not recommender.is_ready:
        print("Failed to initialize system.")
        return

    # Interactive loop or Argument mode
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        print(f"\nAnalyzing: '{text}'")
        result = recommender.predict(text)
        print("\n--- Result ---")
        print(f"Symptoms detected: {result['detected_symptoms']}")
        print(f"Top Recommendations:")
        for spec, score in result['recommendations']:
            print(f"  - {spec}: {score:.1f}")
    else:
        print("\nEnter patient symptoms (or 'q' to quit):")
        while True:
            text = input("> ")
            if text.lower() in ['q', 'quit', 'exit']:
                break
            
            result = recommender.predict(text)
            print(f"Symptoms found: {result['detected_symptoms']}")
            print("Recommendations:")
            for spec, score in result['recommendations']:
                print(f"  {spec} (Score: {score})")
            print("-" * 20)

if __name__ == "__main__":
    main()
