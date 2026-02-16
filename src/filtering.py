import pandas as pd
from typing import List, Dict, Tuple, Optional
from fuzzywuzzy import fuzz, process
import unicodedata
import re
from src.specialty_mapper import SpecialtyMapper
from src.nsga2 import nsga2_rank

class ProviderFilter:
    """
    Filtre les prestataires selon les spécialités recommandées.
    Gère automatiquement la conversion entre noms de spécialités et IDs numériques.
    """
    
    def __init__(self, providers_file: str, specialist_file: str):
        """
        Initialize le filtre avec la base de données des prestataires.
        
        Args:
            providers_file: Chemin vers le fichier Excel des prestataires
            specialist_file: Chemin vers le fichier Excel des spécialistes
        """
        try:
            self.df_providers = pd.read_excel(providers_file)
            self.df_providers.columns = self.df_providers.columns.str.strip()
            print(f"[OK] Prestataires charges : {len(self.df_providers)} enregistrements")
            # Provide column aliases to support different provider file schemas
            # Many datasets use 'consultation_cost' instead of 'average_cost'.
            if 'consultation_cost' in self.df_providers.columns and 'average_cost' not in self.df_providers.columns:
                self.df_providers['average_cost'] = self.df_providers['consultation_cost']
            if 'average_cost' in self.df_providers.columns and 'consultation_cost' not in self.df_providers.columns:
                self.df_providers['consultation_cost'] = self.df_providers['average_cost']
            
            # Charger le mapper de spécialités
            self.mapper = SpecialtyMapper(specialist_file, providers_file)
            print(f"[OK] Mapper de specialites initialise")
            
        except Exception as e:
            print(f"[ERROR] Erreur lors du chargement des prestataires : {e}")
            self.df_providers = None
            self.mapper = None
    
    def filter_by_specialty_name(self, 
                                specialty_name: str, 
                                sort_by: str = 'quality_score',
                                ascending: bool = False,
                                top_n: Optional[int] = None,
                                budget: Optional[float] = None,
                                location: Optional[str] = None,
                                weight_quality: float = 0.5,
                                weight_cost: float = 0.3,
                                weight_proximity: float = 0.2) -> pd.DataFrame:
        """
        Filtre les prestataires par nom de spécialité (ex: "Cardiologist").
        
        Args:
            specialty_name: La spécialité recherchée (nom, ex: "Cardiologist")
            sort_by: Colonne pour le tri ('quality_score', 'waiting_time_days', 'average_cost')
            ascending: Ordre de tri (False = décroissant)
            top_n: Nombre maximal de résultats
            
        Returns:
            DataFrame avec les prestataires filtrés
        """
        if self.df_providers is None or self.mapper is None:
            return pd.DataFrame()
        
        # Support both provider files that store numeric specialty IDs and those that store textual names.
        specialty_col = self.df_providers['specialty'] if 'specialty' in self.df_providers.columns else None

        filtered = pd.DataFrame()
        if specialty_col is None:
            print(f"[ALERT] Colonne 'specialty' manquante dans la base des prestataires")
            return pd.DataFrame()

        # If providers use numeric IDs for specialty, use the mapper to convert name->id
        if pd.api.types.is_numeric_dtype(specialty_col.dtype):
            specialty_id = self.mapper.get_id_by_name(specialty_name)
            if specialty_id is None:
                print(f"[ALERT] Specialite '{specialty_name}' non trouvee dans le mapper (IDs numériques)")
                return pd.DataFrame()

            filtered = self.df_providers[
                self.df_providers['specialty'] == specialty_id
            ].copy()
        else:
            # Providers store specialty as text; perform fuzzy/exact matching on names
            try:
                # Normalize function to remove accents and punctuation
                def _normalize(s: str) -> str:
                    s = str(s).lower().strip()
                    s = unicodedata.normalize('NFKD', s)
                    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
                    s = re.sub(r"[^a-z0-9\s]", ' ', s)
                    s = re.sub(r"\s+", ' ', s).strip()
                    return s

                unique_specs = list(self.df_providers['specialty'].dropna().unique())
                norm_to_orig = { _normalize(x): x for x in unique_specs }
                query_norm = _normalize(specialty_name)

                # Small alias map to correct common typos / role->field mappings
                alias_map = {
                    'internal medcine': 'internal medicine',
                    'internal medecine': 'internal medicine',
                    'internal med': 'internal medicine',
                    'hepatologist': 'gastroenterology',
                    'hepatology': 'gastroenterology',
                    'gastroenterologist': 'gastroenterology'
                }
                # If query matches an alias, map to the provider-side normalized specialty
                if query_norm in alias_map:
                    target_norm = alias_map[query_norm]
                    if target_norm in norm_to_orig:
                        matched = norm_to_orig[target_norm]
                        filtered = self.df_providers[
                            self.df_providers['specialty'].astype(str).str.lower() == str(matched).lower()
                        ].copy()
                        # short-circuit successful alias mapping
                        if not filtered.empty:
                            return filtered

                # Try exact normalized match first
                if query_norm in norm_to_orig:
                    matched = norm_to_orig[query_norm]
                    filtered = self.df_providers[
                        self.df_providers['specialty'].astype(str).str.lower() == str(matched).lower()
                    ].copy()
                else:
                    # Try fuzzy match against normalized names with token_set_ratio
                    choices = list(norm_to_orig.keys())
                    best_norm_tuple = process.extractOne(query_norm, choices, scorer=fuzz.token_set_ratio)
                    if best_norm_tuple:
                        best_norm, score = best_norm_tuple
                    else:
                        best_norm, score = None, 0

                    if score >= 45 and best_norm in norm_to_orig:
                        matched = norm_to_orig.get(best_norm)
                        filtered = self.df_providers[
                            self.df_providers['specialty'].astype(str).str.lower() == str(matched).lower()
                        ].copy()
                    else:
                        # Try matching against original (non-normalized) strings
                        try:
                            orig_choices = unique_specs
                            best_orig_tuple = process.extractOne(specialty_name, orig_choices, scorer=fuzz.token_set_ratio)
                            if best_orig_tuple and best_orig_tuple[1] >= 45:
                                matched = best_orig_tuple[0]
                                filtered = self.df_providers[
                                    self.df_providers['specialty'].astype(str).str.lower() == str(matched).lower()
                                ].copy()
                            else:
                                # Use difflib as a last-resort for close matches
                                close = difflib.get_close_matches(specialty_name, orig_choices, n=1, cutoff=0.4)
                                if close:
                                    matched = close[0]
                                    filtered = self.df_providers[
                                        self.df_providers['specialty'].astype(str).str.lower() == str(matched).lower()
                                    ].copy()
                                else:
                                    # Heuristic: convert '-ologist' -> '-ology' (gastroenterologist -> gastroenterology)
                                    heuristic = re.sub(r'(ologist)$', 'ology', query_norm)
                                    if heuristic in norm_to_orig:
                                        matched = norm_to_orig[heuristic]
                                        filtered = self.df_providers[
                                            self.df_providers['specialty'].astype(str).str.lower() == str(matched).lower()
                                        ].copy()
                                    else:
                                        print(f"[ALERT] Aucun rapprochement fiable pour la specialite '{specialty_name}' (norm_score={score})")
                                        # For debugging, print best candidates
                                        print(f"DEBUG: query_norm={query_norm} best_norm={best_norm} score={score} best_orig={best_orig_tuple if 'best_orig_tuple' in locals() else None}")
                                        return pd.DataFrame()
                        except Exception:
                            print(f"[ALERT] Erreur pendant le rapprochement pour '{specialty_name}'")
                            return pd.DataFrame()
            except Exception:
                # Fallback to simple case-insensitive exact match
                filtered = self.df_providers[
                    self.df_providers['specialty'].astype(str).str.lower() == specialty_name.lower()
                ].copy()
        
        if filtered.empty:
            # Avoid referencing specialty_id which may not be defined in text-specialty branch
            print(f"[ALERT] Aucun prestataire trouve pour {specialty_name} (apres matching nom)")
            return pd.DataFrame()
        
        print(f"[DEBUG] Prestataires trouves pour '{specialty_name}' (avant filtres): {len(filtered)}")

        # Filtrer par budget
        if budget is not None:
            cost_col = 'average_cost' if 'average_cost' in filtered.columns else ('consultation_cost' if 'consultation_cost' in filtered.columns else None)
            
            if cost_col:
                filtered_budget = filtered[filtered[cost_col] <= float(budget)].copy()
                if filtered_budget.empty:
                    print(f"[WARN] Aucun prestataire sous le budget {budget} pour '{specialty_name}'. Affichage des 5 moins chers.")
                    filtered = filtered.sort_values(by=cost_col).head(5)
                else:
                    filtered = filtered_budget.copy()
                    print(f"[DEBUG] Prestataires apres budget ({budget}): {len(filtered)}")

        # Si la localisation est fournie
        location_col = None
        for col in ['city', 'location', 'address']:
            if col in filtered.columns:
                location_col = col
                break

        if location is not None and location_col is not None and not filtered.empty:
            before_loc = len(filtered)
            try:
                filtered['_location_score'] = filtered[location_col].fillna('').astype(str).apply(
                    lambda v: fuzz.token_set_ratio(str(v), str(location))
                )
                print(f"[DEBUG] Location scores computed for '{location}'. Range: {filtered['_location_score'].min()}-{filtered['_location_score'].max()}")
                
                # If specifically requested, we could filter strictly. But for now, we just score them.
                # However, if NSGA2 is used, we want to ensure proximity is considered.
                # Let's warn if all are far.
                if (filtered['_location_score'] < 30).all():
                     print(f"[WARN] Attention: Aucun prestataire vraiment proche de '{location}' (tous scores < 30).")
            except Exception:
                filtered['_location_score'] = 0


        # Normaliser les composantes pour la combinaison pondérée
        # quality (assume 0-5), cost (lower better), proximity (0-100 from fuzz)
        if 'quality_score' in filtered.columns:
            try:
                max_q = filtered['quality_score'].max()
                if max_q and max_q > 0:
                    filtered['_quality_norm'] = filtered['quality_score'] / max_q
                else:
                    filtered['_quality_norm'] = 0
            except Exception:
                filtered['_quality_norm'] = 0
        else:
            filtered['_quality_norm'] = 0

        if 'average_cost' in filtered.columns:
            try:
                min_c = filtered['average_cost'].min()
                max_c = filtered['average_cost'].max()
                if max_c != min_c:
                    # lower cost should yield higher normalized score
                    filtered['_cost_norm'] = (max_c - filtered['average_cost']) / (max_c - min_c)
                else:
                    filtered['_cost_norm'] = 0
            except Exception:
                filtered['_cost_norm'] = 0
        else:
            filtered['_cost_norm'] = 0

        if '_location_score' in filtered.columns:
            try:
                filtered['_proximity_norm'] = filtered['_location_score'] / 100.0
            except Exception:
                filtered['_proximity_norm'] = 0
        else:
            filtered['_proximity_norm'] = 0

        # Calcul du score combiné pondéré
        try:
            filtered['_combined_score'] = (
                weight_quality * filtered.get('_quality_norm', 0).fillna(0)
                + weight_cost * filtered.get('_cost_norm', 0).fillna(0)
                + weight_proximity * filtered.get('_proximity_norm', 0).fillna(0)
            )
        except Exception:
            filtered['_combined_score'] = 0

        # Tri: si un score combiné est présent et les poids sont pertinents, trier par celui-ci
        sort_keys = []
        ascend_list = []
        if '_combined_score' in filtered.columns and (weight_quality + weight_cost + weight_proximity) > 0:
            sort_keys.append('_combined_score')
            ascend_list.append(False)

        if sort_by in filtered.columns:
            sort_keys.append(sort_by)
            ascend_list.append(ascending)

        if sort_keys:
            filtered = filtered.sort_values(by=sort_keys, ascending=ascend_list)
        
        # Limitation du nombre de résultats
        if top_n:
            filtered = filtered.head(top_n)

        # Nettoyer colonnes temporaires
        for c in ['_location_score', '_quality_norm', '_cost_norm', '_proximity_norm', '_combined_score']:
            if c in filtered.columns:
                filtered = filtered.drop(columns=[c])

        return filtered
    
    def filter_by_specialty_id(self, 
                              specialty_id: int, 
                              sort_by: str = 'quality_score',
                              ascending: bool = False,
                              top_n: Optional[int] = None) -> pd.DataFrame:
        """
        Filtre les prestataires par ID de spécialité numérique.
        
        Args:
            specialty_id: L'ID numérique de la spécialité
            sort_by: Colonne pour le tri
            ascending: Ordre de tri
            top_n: Nombre maximal de résultats
            
        Returns:
            DataFrame avec les prestataires filtrés
        """
        if self.df_providers is None:
            return pd.DataFrame()
        
        filtered = self.df_providers[
            self.df_providers['specialty'] == specialty_id
        ].copy()
        
        if sort_by in filtered.columns:
            filtered = filtered.sort_values(by=sort_by, ascending=ascending)
        
        if top_n:
            filtered = filtered.head(top_n)
        
        return filtered
    
    def get_top_providers(self, 
                         specialties: List[str],
                         top_n: int = 10,
                         sort_by: str = 'quality_score',
                         budget: Optional[float] = None,
                         location: Optional[str] = None,
                         weight_quality: float = 0.5,
                         weight_cost: float = 0.3,
                         weight_proximity: float = 0.2) -> Dict[str, pd.DataFrame]:
        """
        Filtre les meilleurs prestataires pour une liste de spécialités.
        
        Args:
            specialties: Liste des noms de spécialités recommandées
            top_n: Nombre de prestataires à retourner par spécialité
            sort_by: Critère de tri
            
        Returns:
            Dictionnaire {spécialité: DataFrame des prestataires}
        """
        results = {}
        
        for specialty in specialties:
            filtered = self.filter_by_specialty_name(
                specialty, 
                top_n=top_n, 
                sort_by=sort_by,
                ascending=(sort_by != 'quality_score'),
                budget=budget,
                location=location,
                weight_quality=weight_quality,
                weight_cost=weight_cost,
                weight_proximity=weight_proximity
            )
            
            if not filtered.empty:
                results[specialty] = filtered
        
        return results

    def optimize_providers_nsga(self,
                                specialty: str,
                                top_k: int = 3,
                                budget: Optional[float] = None,
                                location: Optional[str] = None) -> pd.DataFrame:
        """Return top_k providers for `specialty` using NSGA-II ranking on multiple objectives.

        Objectives used (minimization):
        - cost (average_cost)
        - waiting_time_days
        - -quality_score (we negate quality to turn into minimization)
        - -proximity (higher is better; use -_location_score)
        """
        # First get filtered candidates using existing filters (budget, location)
        candidates = self.filter_by_specialty_name(specialty, top_n=None, budget=budget, location=location)
        if candidates.empty:
            return candidates

        # Ensure required columns
        # Create proximity score if location provided and city-like column exists
        location_col = None
        for col in ['city', 'location', 'address']:
            if col in candidates.columns:
                location_col = col
                break

        if location is not None and location_col is not None:
            candidates['_location_score'] = candidates[location_col].fillna('').astype(str).apply(
                lambda v: fuzz.token_set_ratio(str(v), str(location))
            )
        else:
            candidates['_location_score'] = 0

        # Fill missing numeric columns with sensible defaults
        if 'average_cost' not in candidates.columns:
            candidates['average_cost'] = 0
        if 'waiting_time_days' not in candidates.columns:
            candidates['waiting_time_days'] = candidates.get('waiting_time_days', 0)
        if 'quality_score' not in candidates.columns:
            candidates['quality_score'] = 0

        # Build objective matrix (minimization)
        # cost, waiting_time, -quality, -proximity
        objs = candidates[['average_cost', 'waiting_time_days']].copy().to_numpy(dtype=float)
        quality = -candidates['quality_score'].astype(float).to_numpy()
        proximity = -candidates['_location_score'].astype(float).to_numpy()
        objs = np.hstack([objs, quality.reshape(-1, 1), proximity.reshape(-1, 1)])

        # Use NSGA2 ranking to order indices
        try:
            order = nsga2_rank(objs)
        except Exception:
            # Fallback: sort by quality descending then cost ascending
            order = list(candidates.sort_values(by=['quality_score', 'average_cost'], ascending=[False, True]).index)

        # order contains integer indices relative to candidates' positional index (0..n-1)
        ordered_df = candidates.reset_index(drop=True).iloc[order]

        # Return top_k
        return ordered_df.head(top_k).drop(columns=[c for c in ['_location_score'] if c in ordered_df.columns])
    
    def get_provider_details(self, provider_id: int) -> Dict:
        """
        Récupère les détails complets d'un prestataire.
        
        Args:
            provider_id: ID du prestataire
            
        Returns:
            Dictionnaire avec les détails du prestataire
        """
        if self.df_providers is None:
            return {}
        
        result = self.df_providers[self.df_providers['provider_id'] == provider_id]
        if result.empty:
            return {}
        
        return result.iloc[0].to_dict()
    
    def get_statistics(self, specialty_name: str) -> Dict:
        """
        Récupère les statistiques pour une spécialité donnée.
        
        Args:
            specialty_name: Le nom de la spécialité
            
        Returns:
            Dictionnaire avec les statistiques
        """
        if self.df_providers is None or self.mapper is None:
            return {}
        
        specialty_id = self.mapper.get_id_by_name(specialty_name)
        if specialty_id is None:
            return {}
        
        filtered = self.df_providers[self.df_providers['specialty'] == specialty_id]
        
        if filtered.empty:
            return {}
        
        return {
            'count': len(filtered),
            'avg_cost': filtered['average_cost'].mean(),
            'avg_waiting_time': filtered['waiting_time_days'].mean(),
            'avg_quality_score': filtered['quality_score'].mean(),
            'min_cost': filtered['average_cost'].min(),
            'max_cost': filtered['average_cost'].max(),
        }
