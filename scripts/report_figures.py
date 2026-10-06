"""Figures of the experiment report that no other script draws.

* ``outputs/cohort_positive_rate.png`` – next-month activity rate per signup cohort, before and
  after dropping ``badge_OCZE``, against the test rate implied by the leaderboard.
* ``outputs/cv_f1_summary.png`` – 5-fold F1 of every model (from ``outputs/cv_scores.csv``,
  written by ``scripts/run_cv.py``).

Usage::

    python3 scripts/report_figures.py
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
import seaborn as sns  # noqa: E402

from src.data import MONTH_ORDER, build_xy, load_raw  # noqa: E402

OUTPUT_DIR = ROOT / "outputs"
LEADERBOARD_ALL_ONES_F1 = 0.25
"""All-ones F1 on the official leaderboard (reported by the user)."""

INK, INK_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
C1, C2, GREY = "#2a78d6", "#eb6834", "#a3a29c"


def theme() -> None:
    sns.set_theme(style="whitegrid", rc={"axes.facecolor": SURFACE, "figure.facecolor": SURFACE,
                                         "grid.color": GRID, "text.color": INK, "axes.labelcolor": INK_2,
                                         "xtick.color": INK, "ytick.color": INK_2})


def cohort_positive_rate() -> None:
    rows = []
    for label, excluded in (("raw labels", ()), ("badge_OCZE removed", ("badge_OCZE",))):
        xy = build_xy(load_raw(exclude_titles=excluded))
        y = xy.y[xy.labelled]
        for t, rate in y.groupby(y.index.get_level_values("t")).mean().items():
            rows.append({"cohort": f"M{MONTH_ORDER[t]}", "labels": label, "rate": rate})
    df = pd.DataFrame(rows)
    p_test = LEADERBOARD_ALL_ONES_F1 / (2 - LEADERBOARD_ALL_ONES_F1)

    fig, ax = plt.subplots(figsize=(9, 4.4))
    sns.barplot(data=df, x="cohort", y="rate", hue="labels", palette=[GREY, C1], ax=ax)
    for c in ax.containers:
        ax.bar_label(c, labels=[f"{v:.0%}" for v in c.datavalues], padding=3, fontsize=9)
    ax.axhline(p_test, color=C2, linestyle="--", linewidth=1.5)
    ax.annotate(f"test cohort M4 ≈ {p_test:.0%}\n(implied by the leaderboard all-ones F1 = {LEADERBOARD_ALL_ONES_F1})",
                xy=(3.5, p_test), xytext=(3.0, 0.42), ha="center", fontsize=9, color=C2,
                arrowprops={"arrowstyle": "->", "color": C2, "linewidth": 1})
    ax.set(ylim=(0, 0.9), xlabel="signup cohort", ylabel="")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(title="", frameon=False, loc="upper right")
    ax.set_title("Next-month activity rate per signup cohort: only M12 is out of line",
                 loc="left", fontsize=11)
    sns.despine(left=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "cohort_positive_rate.png", dpi=150)


def cv_f1_summary() -> None:
    scores = pd.read_csv(OUTPUT_DIR / "cv_scores.csv")
    scores = scores[scores.model.str.contains("no badge_OCZE")].copy()
    scores["model"] = scores.model.str.replace(r" \[no badge_OCZE\]", "", regex=True) \
                                  .str.replace(r" \[no badge_OCZE, by type\]", " (by type)", regex=True)
    order = scores.groupby("model", sort=False).F1.mean().index.tolist()
    base = scores[scores.model == "all_ones"].F1.mean()

    fig, ax = plt.subplots(figsize=(9, 4.4))
    palette = {m: (GREY if m in ("all_ones", "logreg_per_page", "decision_tree") else C1) for m in order}
    sns.barplot(data=scores, y="model", x="F1", order=order, hue="model", palette=palette, errorbar="sd",
                capsize=0.25, err_kws={"linewidth": 1, "color": INK_2}, legend=False, ax=ax)
    stats = scores.groupby("model", sort=False).F1.agg(["mean", "std"]).reindex(order)
    for i, (m, sd) in enumerate(zip(stats["mean"], stats["std"])):
        ax.text(m + sd + 0.01, i, f"{m:.3f}", va="center", fontsize=9, color=INK)
    ax.axvline(base, color=C2, linestyle="--", linewidth=1.2)
    ax.text(base + 0.005, len(order) - 0.45, "all-ones", color=C2, fontsize=9)
    ax.set(xlim=(0, 0.6), xlabel="F1, 5-fold CV (mean ± sd), badge_OCZE removed", ylabel="")
    ax.set_title("Class weighting and tuning lift both models above the all-ones line",
                 loc="left", fontsize=11)
    sns.despine(left=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "cv_f1_summary.png", dpi=150)


def main() -> None:
    theme()
    cohort_positive_rate()
    cv_f1_summary()


if __name__ == "__main__":
    main()
