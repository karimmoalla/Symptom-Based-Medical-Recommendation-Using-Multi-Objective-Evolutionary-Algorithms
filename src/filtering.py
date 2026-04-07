import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional

from src.nsga2 import nsga2_rank

class ProviderFilter:
    """
    Filtre les prestataires selon la nouvelle base K2 et K3 (7 features).
    """

    def __init__(self, providers_file: str, specialist_file: str):
        try:
            # On ignore la première ligne qui contient le titre de la base K2
            self.df_providers = pd.read_excel(providers_file, sheet_name='Médecins', skiprows=1)
            
            # Renommer les colonnes pour que l'ancien code ne casse pas, tout en gardant l'info
            column_mapping = {
                'Nom complet': 'provider_name',
                'Spécialité': 'specialty',
                'Ville': 'location',
                'Score qualité': 'quality_score',
                'Coût consult. (TND)': 'average_cost',
                'Délai RDV (jours)': 'waiting_time_days',
                'Téléconsult.': 'teleconsultation',
                'Créneaux/sem.': 'available_slots',
                'CNAM': 'accepts_cnam'
            }
            self.df_providers.rename(columns=column_mapping, inplace=True)
            
            # Conversion des valeurs textuelles (Oui/Non) en booléens
            for col in ['teleconsultation', 'accepts_cnam']:
                if col in self.df_providers.columns:
                    self.df_providers[col] = self.df_providers[col].apply(
                        lambda x: 1 if str(x).strip().lower() == 'oui' else 0
                    )

            self.is_ready = True

        except Exception as e:
            self.df_providers = None
            self.is_ready = False

    def filter_by_specialty_name(self, specialty_name: str, sort_by: str = 'quality_score', ascending: bool = False, top_n: Optional[int] = None) -> pd.DataFrame:
        if not self.is_ready or self.df_providers is None:
            return pd.DataFrame()
            
        # Filtre exact (les noms correspondent exactement car K1 et K2 sont alignés)
        mask = self.df_providers['specialty'].str.lower() == specialty_name.lower()
        filtered = self.df_providers[mask].copy()
        
        if filtered.empty:
            return pd.DataFrame()
            
        if sort_by in filtered.columns:
            filtered = filtered.sort_values(by=sort_by, ascending=ascending)
            
        if top_n is not None:
            filtered = filtered.head(top_n)
            
        return filtered

    def get_top_providers(self, specialties: List[str], top_n: int = 5, sort_by: str = 'quality_score', budget: float = None, location: str = None, weight_quality: float = 0.5, weight_cost: float = 0.3, weight_proximity: float = 0.2) -> Dict[str, pd.DataFrame]:
        results = {}
        for spec in specialties:
            filtered = self.filter_by_specialty_name(spec, sort_by=sort_by, ascending=False, top_n=top_n)
            if not filtered.empty:
                results[spec] = filtered
        return results

    def optimize_providers_nsga(self, specialty_name: str, top_k: int = 3, budget: float = None, location: str = None) -> pd.DataFrame:
        """
        K3/K4/K5 Optimisation NSGA-II sur les 7 paramètres du médecin.
        1. Qualité (à maximiser)
        2. Coût (à minimiser ou optimiser autour du budget)
        3. Délai RDV (à minimiser)
        4. Créneaux (à maximiser)
        5. Distance / Localisation (à minimiser)
        6. CNAM (à maximiser)
        7. Téléconsultation (à maximiser)
        """
        filtered = self.filter_by_specialty_name(specialty_name)
        if filtered.empty:
            return pd.DataFrame()
            
        df_opt = filtered.copy()
        n = len(df_opt)
        
        # NSGA-II dans nsga2.py fait une minimisation !
        # Donc tout ce qu'on veut MAXIMISER, on doit le rendre NÉGATIF.
        
        # 1. Quality (MAX -> *-1)
        obj_quality = -df_opt['quality_score'].fillna(0).values
        
        # 2. Cost (MIN -> tel quel, ou distance au budget)
        costs = df_opt['average_cost'].fillna(0).values
        if budget is not None:
            # On minimise la différence absolue (excès)
            obj_cost = np.abs(costs - budget)
        else:
            obj_cost = costs
            
        # 3. Wait time (MIN -> tel quel)
        obj_wait = df_opt['waiting_time_days'].fillna(30).values
        
        # 4. Slots (MAX -> *-1)
        obj_slots = -df_opt['available_slots'].fillna(0).values
        
        # 5. Location (MIN distance -> mock simple si location textuelle)
        if location is not None:
            # Si même ville = distance 0, sinon distance 1
            obj_loc = np.where(df_opt['location'].str.lower() == location.lower(), 0, 1)
        else:
            obj_loc = np.zeros(n)
            
        # 6. CNAM (MAX -> *-1)
        obj_cnam = -df_opt['accepts_cnam'].fillna(0).values
        
        # 7. Téléconsult (MAX -> *-1)
        obj_tele = -df_opt['teleconsultation'].fillna(0).values
        
        # Matrice d'objectifs (N, 7)
        objs = np.column_stack([
            obj_quality,
            obj_cost,
            obj_wait,
            obj_slots,
            obj_loc,
            obj_cnam,
            obj_tele
        ])
        
        try:
            ranked_indices = nsga2_rank(objs)
            # Reordonner le dataframe
            df_opt = df_opt.iloc[ranked_indices]
            return df_opt.head(top_k)
        except Exception as e:
            print(f"Erreur NSGA-II : {e}")
            return df_opt.head(top_k)
