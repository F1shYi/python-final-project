"""Feature elimination: recursive feature elimination with cross-validation (RFECV).

``make_logreg_rfe(X)`` = the balanced logistic regression of :func:`src.models.simple.make_logreg`
whose classifier step is wrapped in ``RFECV``: starting from all (one-hot / scaled) inputs, it
repeatedly fits the model, drops the ``step`` inputs with the smallest absolute coefficients,
scores every feature count by inner K-fold F1, keeps the best count and refits on it.
Used inside :func:`src.eval.cross_validate`, the elimination only sees each outer fold's training
rows (nested cross-validation), like the hyper-parameter search.
"""
from __future__ import annotations

import pandas as pd
from sklearn.feature_selection import RFECV
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline

from src.models.simple import SEED, make_logreg


def make_logreg_rfe(X: pd.DataFrame, step: int = 10, n_splits: int = 5, n_jobs: int = -1,
                    class_weight: str | dict | None = "balanced") -> Pipeline:
    """Balanced logistic regression with RFECV on its preprocessed inputs.

    Parameters
    ----------
    step:
        Inputs removed per elimination round.
    n_splits:
        Inner folds used to score each feature count (F1).
    """
    pipe = make_logreg(X, class_weight=class_weight)
    rfe = RFECV(pipe.named_steps["clf"], step=step, min_features_to_select=1,
                cv=StratifiedKFold(n_splits, shuffle=True, random_state=SEED), scoring="f1", n_jobs=n_jobs)
    return Pipeline([("prep", pipe.named_steps["prep"]), ("clf", rfe)])


def rfe_curve(model: Pipeline) -> pd.DataFrame:
    """Fitted :func:`make_logreg_rfe` → inner-CV F1 (mean, std) per number of kept inputs."""
    res = model.named_steps["clf"].cv_results_
    return pd.DataFrame({"n_features": res["n_features"], "F1_mean": res["mean_test_score"],
                         "F1_std": res["std_test_score"]})


def selected_features(model: Pipeline) -> pd.Series:
    """Fitted :func:`make_logreg_rfe` → coefficient of every kept input, largest |coef| first."""
    names = model.named_steps["prep"].get_feature_names_out()
    rfe = model.named_steps["clf"]
    coef = pd.Series(rfe.estimator_.coef_[0], index=names[rfe.support_], name="coef")
    return coef.reindex(coef.abs().sort_values(ascending=False).index)
