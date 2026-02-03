import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATA_FILE = os.path.join(BASE_DIR, 'Specialist.xlsx') 

TARGET_COL = 'Disease'  
IGNORED_COLS = ['Unnamed: 0']

LANGUAGE = 'english' 
