import numpy as np
from typing import List

def fast_non_dominated_sort(objs: np.ndarray) -> List[List[int]]:
    """
    Implémentation vectorisée et optimisée du tri Pareto de NSGA-II (Efficacité améliorée).
    Réduit drastiquement le temps d'exécution grâce à Numpy (bypasse les boucles imbriquées).
    """
    n = objs.shape[0]
    
    # Réduction vectorielle des comparaisons (Point 2.a: Fast Non-Dominated Sorting Optimisé)
    diff = objs[:, np.newaxis, :] - objs[np.newaxis, :, :]
    less_equal = np.all(diff <= 0, axis=-1)
    strictly_less = np.any(diff < 0, axis=-1)
    
    domination_matrix = less_equal & strictly_less
    
    # Nombre de solutions qui dominent p
    n_dom = np.sum(domination_matrix, axis=0)
    
    # Solutions que p domine
    S = [np.where(domination_matrix[p, :])[0].tolist() for p in range(n)]
    
    fronts = []
    current_front = np.where(n_dom == 0)[0].tolist()
    
    while current_front:
        fronts.append(current_front)
        next_front = []
        for p in current_front:
            for q in S[p]:
                n_dom[q] -= 1
                if n_dom[q] == 0:
                    next_front.append(q)
        current_front = next_front
        
    return fronts


def knn_density_distance(objs: np.ndarray, front: List[int], k_neighbors: int = 3) -> np.ndarray:
    """
    AMÉLIORATION (Idée 1.c: Densité Améliorée) : Utilisation de la Densité KNN.
    Remplace la Crowding Distance classique. KNN mesure la distance réelle vers les plus proches voisins.
    """
    l = len(front)
    if l <= 1:
        return np.array([np.inf])
    if l <= 2:
        return np.array([np.inf, np.inf])

    k = min(k_neighbors, l - 1)
    F = objs[front, :]

    maxv = F.max(axis=0)
    minv = F.min(axis=0)
    rng = maxv - minv
    rng[rng == 0] = 1.0  
    F_norm = (F - minv) / rng

    diff = F_norm[:, np.newaxis, :] - F_norm[np.newaxis, :, :]
    distances = np.sqrt(np.sum(diff ** 2, axis=-1))
    distances.sort(axis=1)
    
    knn_dist = np.mean(distances[:, 1:k+1], axis=1)

    for m in range(F.shape[1]):
        sorted_idx = np.argsort(F[:, m])
        knn_dist[sorted_idx[0]] = np.inf
        knn_dist[sorted_idx[-1]] = np.inf

    return knn_dist


def nsga2_rank(objs: np.ndarray) -> List[int]:
    """
    Trie l'ensemble des points en combinant la Supériorité Pareto améliorée 
    puis la diversité calculée via KNN-Density.
    C'est la version de NSGA-II améliorée (précision + efficacité améliorée).
    """
    if len(objs) <= 1:
        return [0] if len(objs) == 1 else []

    # 1) Non Dominating Sort (Vitesse améliorée)
    fronts = fast_non_dominated_sort(objs)
    ordered = []

    # 2) Triage intra-front
    for front in fronts:
        if len(front) == 0:
            continue

        if len(front) <= 2:
            ordered.extend(front)
        else:
            # Densité KNN (Précision améliorée)
            distances = knn_density_distance(objs, front, k_neighbors=3)        

            sort_indices = np.argsort(-distances)
            sorted_front = [front[i] for i in sort_indices]
            ordered.extend(sorted_front)

    return ordered
