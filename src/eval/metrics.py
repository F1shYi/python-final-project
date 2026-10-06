"""Evaluation metrics.

Official competition metric: F1 score of the positive class (``Active = 1``) on hard 0/1
predictions, ``F1 = 2 * precision * recall / (precision + recall)``.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score


def f1(y_true: pd.Series | np.ndarray, y_pred: pd.Series | np.ndarray) -> float:
    """F1 score of the positive class.

    Parameters
    ----------
    y_true, y_pred:
        Binary 0/1 labels of the same length. If both are Series, they are aligned on the index.

    Raises
    ------
    ValueError
        If the inputs are not binary, contain NaN, or the Series indices differ.
    """
    if isinstance(y_true, pd.Series) and isinstance(y_pred, pd.Series):
        if not y_true.index.equals(y_pred.index):
            if not y_true.index.sort_values().equals(y_pred.index.sort_values()):
                raise ValueError("y_true and y_pred have different indices")
            y_pred = y_pred.reindex(y_true.index)
    y_true, y_pred = np.asarray(y_true, dtype=float), np.asarray(y_pred, dtype=float)
    for name, a in (("y_true", y_true), ("y_pred", y_pred)):
        if not np.isin(a, (0, 1)).all():
            raise ValueError(f"{name} must contain only 0/1 values (no NaN, no probabilities)")
    return float(f1_score(y_true, y_pred, pos_label=1, zero_division=0))
