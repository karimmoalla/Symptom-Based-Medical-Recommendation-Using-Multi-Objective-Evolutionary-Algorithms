import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Les 4 nouvelles ressources cliniques et d'offre médicale
SPECIALIST_FILE = os.path.join(BASE_DIR, 'Specialist_Enhanced.xlsx')
MODEL_RESULTS_FILE = os.path.join(BASE_DIR, 'Model_Results.xlsx')
K1_TREE_FILE = os.path.join(BASE_DIR, 'K1_Hierarchical_Tree.xlsx')
K2_PROVIDERS_FILE = os.path.join(BASE_DIR, 'K2_Medical_Providers.xlsx')
TARGET_COL = 'Spécialiste'
LANGUAGE = 'english' 

