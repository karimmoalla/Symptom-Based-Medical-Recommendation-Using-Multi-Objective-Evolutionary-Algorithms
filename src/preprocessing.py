import re
import unicodedata

def normalize_text(text: str) -> str:
    """
    Normalize text: lowercase, remove accents, remove punctuation.
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove accents
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    
    # Replace underscores with space (important for user input like 'stomach_pain')
    text = text.replace('_', ' ')

    # Remove punctuation (keep spaces)
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def tokenize(text: str) -> list:
    """
    Simple whitespace tokenization.
    """
    return text.split()
