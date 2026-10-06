"""5-fold random-by-user cross-validation F1 of the models under each data / feature setting.

Usage::

    python3 scripts/run_cv.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from src.data import DatasetSpec, build_xy, kfold_by_user, load_raw  # noqa: E402
from src.data.loading import EXCLUDED_TITLES  # noqa: E402
from src.eval import cross_validate, summarize  # noqa: E402
from src.models import make_all_ones, make_logreg, make_logreg_rfe, make_tree, make_tree_search  # noqa: E402

ALL_MODELS = ("all_ones", "logreg_per_page", "logreg_per_page_balanced", "decision_tree", "decision_tree_tuned")
SETTINGS = [
    # (label, titles excluded at load time, activity feature group, models)
    ("raw", (), "activity_counts", ALL_MODELS),
    ("no badge_OCZE", EXCLUDED_TITLES, "activity_counts", ALL_MODELS + ("logreg_per_page_balanced_rfe",)),
    ("no badge_OCZE, by type", EXCLUDED_TITLES, "activity_counts_by_type", ("decision_tree_tuned",)),
]


def main() -> None:
    scores = []
    for label, excluded, features, names in SETTINGS:
        xy = build_xy(load_raw(exclude_titles=excluded), DatasetSpec(feature_groups=("profile", features)))
        folds = kfold_by_user(xy, 5)
        X_lab = xy.X[xy.labelled]
        models = {
            "all_ones": make_all_ones,
            "logreg_per_page": lambda: make_logreg(X_lab),
            "logreg_per_page_balanced": lambda: make_logreg(X_lab, class_weight="balanced"),
            "decision_tree": lambda: make_tree(X_lab),
            "decision_tree_tuned": lambda: make_tree_search(X_lab),
            "logreg_per_page_balanced_rfe": lambda: make_logreg_rfe(X_lab),
        }
        scores += [cross_validate(models[name], xy, folds, f"{name} [{label}]") for name in names]
    scores = pd.concat(scores, ignore_index=True)
    scores.to_csv(ROOT / "outputs" / "cv_scores.csv", index=False)
    print(summarize(scores))


if __name__ == "__main__":
    main()
