import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATA_FILE = os.path.join(BASE_DIR, 'Specialist.xlsx') 
# Updated providers file (user replaced the providers DB)
PROVIDERS_FILE = os.path.join(BASE_DIR, 'Medical_Providers_International.xlsx')

TARGET_COL = 'Disease'  
IGNORED_COLS = ['Unnamed: 0']

LANGUAGE = 'english' 

