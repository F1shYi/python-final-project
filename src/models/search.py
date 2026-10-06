"""Hyper-parameter search, wrapped as an estimator so it can be cross-validated like any model.

``make_tree_search(X)`` returns a ``GridSearchCV`` that, when fitted, picks the best decision-tree
hyper-parameters by inner K-fold F1 on the data it is given and refits on all of it. Used inside
:func:`src.eval.cross_validate`, the inner search only sees each outer fold's training rows
(nested cross-validation), so the outer score is not biased by the search.
"""
from __future__ import annotations

import pandas as pd
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from src.models.simple import SEED, make_tree

TREE_GRID: dict[str, list] = {
    "max_depth": [2, 3, 4, 5, 6, 8, 10, 15, None],
    "min_samples_leaf": [1, 5, 10, 20, 50, 100],
    "criterion": ["gini", "entropy"],
    "class_weight": [None, "balanced"],
}
"""Search space of :func:`make_tree_search` (216 combinations)."""


def make_tree_search(X: pd.DataFrame, grid: dict[str, list] = TREE_GRID, n_splits: int = 5,
                     n_jobs: int = -1) -> GridSearchCV:
    """Grid search over :data:`TREE_GRID`, scored by F1 with a stratified inner K-fold."""
    return GridSearchCV(
        make_tree(X),
        param_grid={f"clf__{k}": v for k, v in grid.items()},
        scoring="f1",
        cv=StratifiedKFold(n_splits, shuffle=True, random_state=SEED),
        n_jobs=n_jobs,
    )


def search_table(search: GridSearchCV) -> pd.DataFrame:
    """Fitted search → one row per combination (params, mean / std inner F1), best first."""
    res = pd.DataFrame(search.cv_results_)
    params = pd.json_normalize(res.params).rename(columns=lambda c: c.removeprefix("clf__"))
    return (params.assign(F1_mean=res.mean_test_score, F1_std=res.std_test_score, rank=res.rank_test_score)
                  .sort_values("rank").reset_index(drop=True))
