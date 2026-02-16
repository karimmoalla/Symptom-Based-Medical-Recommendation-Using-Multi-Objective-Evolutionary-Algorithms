import pandas as pd
from src.config import PROVIDERS_FILE

path = PROVIDERS_FILE
try:
    df = pd.read_excel(path)
    print('COLUMNS:', df.columns.tolist())
    print('\nHEAD:')
    print(df.head(5).to_string(index=False))
except Exception as e:
    print('ERROR:', e)
