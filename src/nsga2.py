import numpy as np
from typing import List


def fast_non_dominated_sort(objs: np.ndarray) -> List[List[int]]:
    n = objs.shape[0]
    S = [[] for _ in range(n)]
    n_dom = [0] * n
    rank = [0] * n
    fronts = [[]]

    for p in range(n):
        S[p] = []
        n_dom[p] = 0
        for q in range(n):
            if p == q:
                continue
            # p dominates q if p <= q for all and < for at least one (minimization)
            less_equal = np.all(objs[p] <= objs[q])
            strictly_less = np.any(objs[p] < objs[q])
            if less_equal and strictly_less:
                S[p].append(q)
            elif np.all(objs[q] <= objs[p]) and np.any(objs[q] < objs[p]):
                n_dom[p] += 1
        if n_dom[p] == 0:
            rank[p] = 0
            fronts[0].append(p)

    i = 0
    while fronts[i]:
        Q = []
        for p in fronts[i]:
            for q in S[p]:
                n_dom[q] -= 1
                if n_dom[q] == 0:
                    rank[q] = i + 1
                    Q.append(q)
        i += 1
        fronts.append(Q)
    # remove last empty
    if not fronts[-1]:
        fronts.pop()
    return fronts


def crowding_distance(objs: np.ndarray, front: List[int]) -> np.ndarray:
    l = len(front)
    if l == 0:
        return np.array([])
    distances = np.zeros(l)
    F = objs[front, :]
    num_obj = F.shape[1]
    for m in range(num_obj):
        vals = F[:, m]
        sorted_idx = np.argsort(vals)
        maxv = vals.max()
        minv = vals.min()
        if maxv == minv:
            continue
        distances[sorted_idx[0]] = np.inf
        distances[sorted_idx[-1]] = np.inf
        for i in range(1, l - 1):
            distances[sorted_idx[i]] += (vals[sorted_idx[i + 1]] - vals[sorted_idx[i - 1]]) / (maxv - minv)
    return distances


def nsga2_rank(objs: np.ndarray) -> List[int]:
    """Return indices sorted by NSGA-II ranking (fronts then crowding distance desc)."""
    fronts = fast_non_dominated_sort(objs)
    ordered = []
    for front in fronts:
        if len(front) == 0:
            continue
        distances = crowding_distance(objs, front)
        # sort by distance descending (keep extreme points first)
        idxs = np.array(front)[np.argsort(-distances)]
        ordered.extend(list(idxs))
    return ordered
