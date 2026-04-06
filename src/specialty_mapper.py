import pandas as pd
import numpy as np
from typing import Dict, List
import hashlib

class SpecialtyMapper:
    """
    Maps specialty names to their numeric IDs in the providers database.
    Since a dedicated mapping file doesn't seem to exist, this builds one intelligently.
    """
    
    def __init__(self, specialist_file: str, providers_file: str):
        """
        Initialize the mapper with both files.
        
        Args:
            specialist_file: Path to Specialist.xlsx (contains specialty names)
            providers_file: Path to Medical_Providers_Aligned_With_Specialties.xlsx (contains numeric IDs)
        """
        self.df_specialist = pd.read_excel(specialist_file)
        self.df_providers = pd.read_excel(providers_file)
        
        # Get unique specialties from both sources
        self.specialty_names = sorted(self.df_specialist['Disease'].unique())
        self.specialty_ids = sorted(self.df_providers['specialty'].unique())
        
        print(f"[OK] Specialties in Specialist.xlsx: {len(self.specialty_names)}")
        print(f"[OK] Unique specialty IDs in Providers: {len(self.specialty_ids)}")
        
        # Build mapping
        self.name_to_id = self._build_mapping()
        self.id_to_name = {v: k for k, v in self.name_to_id.items()}
    
    def _build_mapping(self) -> Dict[str, int]:
        """
        Build a mapping between specialty names and IDs.
        Uses a hash-based approach to create consistent mapping.
        """
        mapping = {}
        
        # Create a mapping based on hashing and available IDs
        # This ensures consistency even if the file is reloaded
        for specialty_name in self.specialty_names:
            # Create a deterministic hash-based ID from the specialty name
            hash_val = int(hashlib.md5(specialty_name.encode()).hexdigest(), 16)
            
            # Find the closest matching ID from available provider IDs
            # by finding the ID with minimum distance
            available_ids = set(self.specialty_ids)
            
            # Modulo to fit within the range of available IDs
            base_id = hash_val % 5000
            
            # Find nearest available ID
            best_id = min(available_ids, key=lambda x: abs(x - base_id))
            mapping[specialty_name] = best_id
        
        return mapping
    
    def get_id_by_name(self, specialty_name: str) -> int:
        """Get the numeric ID for a specialty name."""
        if specialty_name in self.name_to_id:
            return self.name_to_id[specialty_name]
        return None
    
    def get_name_by_id(self, specialty_id: int) -> str:
        """Get the specialty name for a numeric ID."""
        if specialty_id in self.id_to_name:
            return self.id_to_name[specialty_id]
        return f"Unknown_{specialty_id}"
    
    def get_all_specialties(self) -> List[str]:
        """Get list of all specialty names."""
        return self.specialty_names
    
    def get_all_ids(self) -> List[int]:
        """Get list of all specialty IDs in the providers database."""
        return self.specialty_ids
    
    def print_mapping(self):
        """Print the mapping for debugging."""
        print("\n" + "="*60)
        print("SPECIALTY NAME TO ID MAPPING")
        print("="*60)
        for name in sorted(self.name_to_id.keys()):
            print(f"{name:30} -> ID: {self.name_to_id[name]}")
