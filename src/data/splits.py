"""Train / validation splits of an :class:`~src.data.dataset.XY`.

* :func:`kfold_by_user` – random K-fold over users: every user is in exactly one validation
  fold, and all samples of a user stay on the same side (relevant once a sampler produces
  several samples per user).
* :func:`test_set` – the competition test rows (users of ``SampleSubmission.csv``, no label).

Only labelled rows are split; which rows are labelled is decided by the label definition.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold

from src.data.dataset import XY, submission_user_ids
from src.data.loading import RawData

SEED = 42


@dataclass(frozen=True)
class Fold:
    """One split: index labels (``(User_ID, t)``) of the training and validation rows."""

    k: int
    train_index: pd.MultiIndex
    valid_index: pd.MultiIndex

    def train(self, xy: XY) -> tuple[pd.DataFrame, pd.Series]:
        """``X, y`` of the training rows."""
        return xy.X.loc[self.train_index], xy.y.loc[self.train_index].astype(int)

    def valid(self, xy: XY) -> tuple[pd.DataFrame, pd.Series]:
        """``X, y`` of the validation rows."""
        return xy.X.loc[self.valid_index], xy.y.loc[self.valid_index].astype(int)


def kfold_by_user(xy: XY, n_splits: int = 5, seed: int = SEED, stratify: bool = True) -> list[Fold]:
    """Random K-fold of the labelled rows, grouped by ``User_ID``.

    Parameters
    ----------
    n_splits:
        Number of folds K.
    seed:
        Shuffling seed; the same seed gives the same folds.
    stratify:
        Keep the positive rate of every fold close to the overall rate.
    """
    labelled = xy.y[xy.labelled]
    users = labelled.index.get_level_values("User_ID")
    splitter = (StratifiedGroupKFold(n_splits, shuffle=True, random_state=seed) if stratify
                else GroupKFold(n_splits, shuffle=True, random_state=seed))
    return [Fold(k=k, train_index=labelled.index[tr], valid_index=labelled.index[va])
            for k, (tr, va) in enumerate(splitter.split(labelled, labelled.astype(int), groups=users))]


def test_set(xy: XY, raw: RawData) -> pd.DataFrame:
    """Rows of ``X`` for the users in ``SampleSubmission.csv`` (no target available)."""
    ids = submission_user_ids(raw)
    test = xy.X[xy.X.index.get_level_values("User_ID").isin(ids) & ~xy.labelled]
    assert test.index.get_level_values("User_ID").is_unique, "several test rows per submission user"
    return test


def folds_table(xy: XY, folds: list[Fold]) -> pd.DataFrame:
    """Size and positive rate of every fold (for a quick check)."""
    return pd.DataFrame([{
        "fold": f.k,
        "n_train": len(f.train_index), "n_valid": len(f.valid_index),
        "pos_rate_train": xy.y.loc[f.train_index].mean(), "pos_rate_valid": xy.y.loc[f.valid_index].mean(),
    } for f in folds]).set_index("fold").round(3)
