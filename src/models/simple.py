"""Simple models, as scikit-learn estimators built by zero-argument factories.

* :func:`make_all_ones` – predicts "active" for everybody (reference line for F1).
* :func:`make_logreg` – logistic regression; categorical columns are one-hot encoded and
  numeric columns standardised, which the model itself requires (no feature engineering).
* :func:`make_tree` – decision tree with scikit-learn defaults; categorical columns are
  integer-coded, numeric columns are used as they are.
"""
from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

SEED = 42


def make_all_ones() -> DummyClassifier:
    """Always predicts class 1."""
    return DummyClassifier(strategy="constant", constant=1)


def make_logreg(X: pd.DataFrame, C: float = 1.0, max_iter: int = 2000,
                class_weight: str | dict | None = None) -> Pipeline:
    """Logistic regression on the columns of ``X`` (categorical dtype → one-hot, others → scaled).

    Parameters
    ----------
    X:
        Used only to find the categorical / numeric columns.
    C:
        Inverse L2 regularisation strength.
    class_weight:
        ``None`` → every sample weighs 1; ``"balanced"`` → samples weighted inversely to their
        class frequency (with ~1:4 positives:negatives, a positive weighs ~4× a negative).
    """
    categorical = [c for c in X.columns if isinstance(X[c].dtype, pd.CategoricalDtype)]
    numeric = [c for c in X.columns if c not in categorical]
    prep = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", StandardScaler(), numeric),
    ])
    return Pipeline([("prep", prep),
                     ("clf", LogisticRegression(C=C, max_iter=max_iter, class_weight=class_weight,
                                                    random_state=SEED))])


def make_tree(X: pd.DataFrame, **params) -> Pipeline:
    """Decision tree (CART, Gini) on the columns of ``X``; ``params`` go to ``DecisionTreeClassifier``.

    Categorical columns are mapped to integer codes (missing / unseen → -1); numeric columns pass through.
    """
    categorical = [c for c in X.columns if isinstance(X[c].dtype, pd.CategoricalDtype)]
    numeric = [c for c in X.columns if c not in categorical]
    prep = ColumnTransformer([
        ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1,
                               encoded_missing_value=-1), categorical),
        ("num", "passthrough", numeric),
    ])
    return Pipeline([("prep", prep), ("clf", DecisionTreeClassifier(random_state=SEED, **params))])
