"""Cross-validation: fit a fresh model on every fold's training rows and score its validation rows."""
from __future__ import annotations

from typing import Callable

import pandas as pd
from sklearn.base import BaseEstimator

from src.data.dataset import XY
from src.data.splits import Fold
from src.eval.metrics import f1


def cross_validate(factory: Callable[[], BaseEstimator], xy: XY, folds: list[Fold], name: str) -> pd.DataFrame:
    """F1 of ``factory()`` on every fold (hard predictions from ``model.predict``).

    Returns one row per fold: ``model, fold, n_train, n_valid, F1``.
    """
    rows = []
    for fold in folds:
        X_tr, y_tr = fold.train(xy)
        X_va, y_va = fold.valid(xy)
        model = factory().fit(X_tr, y_tr)
        y_pred = pd.Series(model.predict(X_va), index=y_va.index)
        rows.append({"model": name, "fold": fold.k, "n_train": len(y_tr), "n_valid": len(y_va),
                     "F1": f1(y_va, y_pred)})
    return pd.DataFrame(rows)


def summarize(scores: pd.DataFrame) -> pd.DataFrame:
    """Mean and standard deviation of F1 over folds, per model."""
    return scores.groupby("model", sort=False).F1.agg(["mean", "std"]).round(3)
