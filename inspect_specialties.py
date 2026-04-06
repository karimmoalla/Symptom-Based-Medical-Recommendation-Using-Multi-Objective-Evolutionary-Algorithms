#!/usr/bin/env python
from src.config import PROVIDERS_FILE
import pandas as pd

try:
    df = pd.read_excel(PROVIDERS_FILE)
    if 'specialty' not in df.columns:
        print("Column 'specialty' not found in providers file. Columns:")
        print(list(df.columns))
    else:
        vals = df['specialty'].dropna().unique()
        print("SPECIALTY_DTYPE:", df['specialty'].dtype)
        print("SPECIALTY VALUES (up to 200):")
        for v in vals[:200]:
            print(v)
except Exception as e:
    print('ERROR:', e)
