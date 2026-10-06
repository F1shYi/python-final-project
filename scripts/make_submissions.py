"""Predict the test users with each method and save one submission CSV per method in ``outputs/``.

Settings (file-name suffix): raw click log (none), :data:`src.data.loading.EXCLUDED_TITLES` removed
(``_no_badge``), and additionally page titles counted per page type (``_no_badge_by_type``).

Usage::

    python3 scripts/make_submissions.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data import DatasetSpec, build_xy, load_raw  # noqa: E402
from src.data.loading import EXCLUDED_TITLES  # noqa: E402
from src.models import (make_all_ones, make_logreg, make_logreg_rfe, make_tree, make_tree_search,  # noqa: E402
                        rfe_curve, search_table, selected_features)
from src.submission import make_submission  # noqa: E402

OUTPUT_DIR = ROOT / "outputs"


ALL_MODELS = ("all_ones", "logreg_per_page", "logreg_per_page_balanced", "decision_tree", "decision_tree_tuned")
SETTINGS = [
    # (file-name suffix, titles excluded at load time, activity feature group, models)
    ("", (), "activity_counts", ALL_MODELS),
    ("_no_badge", EXCLUDED_TITLES, "activity_counts", ALL_MODELS + ("logreg_per_page_balanced_rfe",)),
    ("_no_badge_by_type", EXCLUDED_TITLES, "activity_counts_by_type", ("decision_tree_tuned",)),
]


def main() -> None:
    for suffix, excluded, features, names in SETTINGS:
        raw = load_raw(exclude_titles=excluded)
        xy = build_xy(raw, DatasetSpec(feature_groups=("profile", features)))
        X_lab = xy.X[xy.labelled]
        models = {"all_ones": make_all_ones, "logreg_per_page": lambda: make_logreg(X_lab),
                  "logreg_per_page_balanced": lambda: make_logreg(X_lab, class_weight="balanced"),
                  "decision_tree": lambda: make_tree(X_lab), "decision_tree_tuned": lambda: make_tree_search(X_lab),
                  "logreg_per_page_balanced_rfe": lambda: make_logreg_rfe(X_lab)}
        for name in names:
            model = models[name]()
            sub = make_submission(model, xy, raw, OUTPUT_DIR / f"submission_{name}{suffix}.csv")
            print(f"{name + suffix:40s} rows={len(sub)}  predicted active={sub.Active.sum()} ({sub.Active.mean():.1%})")
            if name == "decision_tree_tuned":
                search_table(model).to_csv(OUTPUT_DIR / f"tree_search{suffix}.csv", index=False)
                print(f"  best tree params{suffix}: {model.best_params_}  inner F1={model.best_score_:.3f}")
            if name == "logreg_per_page_balanced_rfe":
                curve = rfe_curve(model)
                curve.to_csv(OUTPUT_DIR / f"rfe_curve{suffix}.csv", index=False)
                selected_features(model).to_csv(OUTPUT_DIR / f"rfe_selected{suffix}.csv")
                best = curve.loc[curve.F1_mean.idxmax()]
                print(f"  RFE{suffix}: kept {int(best.n_features)} of {int(curve.n_features.max())} inputs, "
                      f"inner F1={best.F1_mean:.3f}")


if __name__ == "__main__":
    main()
