"""Draw the best decision tree found so far.

Best tree = rank 1 of ``outputs/tree_search_no_badge_by_type.csv`` (written by
``scripts/make_submissions.py``): badge_OCZE removed, page views counted per page type,
refitted on all labelled users.

Usage::

    python3 scripts/plot_best_tree.py

Output: ``outputs/best_tree.png`` and ``outputs/best_tree.svg``.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.tree import plot_tree  # noqa: E402

from src.data import DatasetSpec, build_xy, load_raw  # noqa: E402
from src.models import make_tree  # noqa: E402

OUTPUT_DIR = ROOT / "outputs"


def best_params() -> dict:
    best = pd.read_csv(OUTPUT_DIR / "tree_search_no_badge_by_type.csv").iloc[0]
    return {"max_depth": int(best.max_depth), "min_samples_leaf": int(best.min_samples_leaf),
            "criterion": best.criterion,
            "class_weight": None if pd.isna(best.class_weight) else best.class_weight}


def readable(name: str) -> str:
    """``num__act_join_comp`` → ``join_comp``; ``cat__Countries_ID`` → ``Countries_ID (code)``."""
    kind, col = name.split("__", 1)
    col = col.removeprefix("act_")
    return f"{col} (code)" if kind == "cat" else col


def main() -> None:
    xy = build_xy(load_raw(), DatasetSpec(feature_groups=("profile", "activity_counts_by_type")))
    X, y = xy.X[xy.labelled], xy.y[xy.labelled].astype(int)
    params = best_params()
    model = make_tree(X, **params).fit(X, y)
    tree = model.named_steps["clf"]
    names = [readable(n) for n in model.named_steps["prep"].get_feature_names_out()]

    fig, ax = plt.subplots(figsize=(44, 13))
    plot_tree(tree, feature_names=names, class_names=["inactive", "active"], filled=True, rounded=True,
              impurity=False, proportion=True, precision=2, fontsize=9, ax=ax)
    ax.set_title(f"Best decision tree (depth {tree.get_depth()}, {tree.get_n_leaves()} leaves; "
                 f"max_depth={params['max_depth']}, min_samples_leaf={params['min_samples_leaf']}, "
                 f"{params['criterion']}, class_weight={params['class_weight']})", fontsize=16, loc="left")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "best_tree.png", dpi=110)
    fig.savefig(OUTPUT_DIR / "best_tree.svg")
    print(params, "depth", tree.get_depth(), "leaves", tree.get_n_leaves())


if __name__ == "__main__":
    main()
