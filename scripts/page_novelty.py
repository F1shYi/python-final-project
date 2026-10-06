"""How many competition / blog / job pages seen by test users were never seen in training?

Pages are the ``comp_ID_xxx`` / ``blog_ID_xxx`` / ``job_ID_xxx`` / ``badge_xxx`` titles of the
click log, counted in each user's signup month (the feature window of X).

* Test vs. training: test = M4 cohort, training = labelled cohorts M11–M3.
* Over time: for every cohort, the share of its page views on pages that no earlier cohort saw.

Usage::

    python3 scripts/page_novelty.py

* Training support: for every test page view, how many training users viewed the same page
  (per-page columns) vs. the same page type (by-type columns).

Output: ``outputs/page_novelty.png``, ``outputs/page_support.png`` and the matching CSV files.
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

from src.data import MONTH_ORDER, MONTH_TO_T, build_events, build_users, load_raw  # noqa: E402

OUTPUT_DIR = ROOT / "outputs"
TEST_T = MONTH_TO_T[4]
PAGE_TYPES = ("comp", "blog", "job", "badge")

INK, INK_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
C1, C2 = "#2a78d6", "#eb6834"  # categorical slots 1 and 2


def signup_month_page_views() -> pd.DataFrame:
    """Page-view events in each user's signup month, with ``type`` (comp / blog / job / badge)."""
    raw = load_raw()
    users = build_users(raw)
    ev = build_events(raw).merge(users[["t0"]], left_on="User_ID", right_index=True)
    ev = ev[(ev.t == ev.t0) & (ev.source == "activity")].copy()
    ev["type"] = ev.title.str.extract(rf"^({'|'.join(PAGE_TYPES)})_")[0]
    return ev.dropna(subset=["type"])


def test_vs_training(pages: pd.DataFrame) -> pd.DataFrame:
    """Per page type: distinct pages of the test cohort, how many are new, and the share of views on them."""
    train, test = pages[pages.t0 < TEST_T], pages[pages.t0 == TEST_T]
    rows = []
    for ty in PAGE_TYPES:
        seen = set(train.loc[train.type == ty, "title"])
        tv = test[test.type == ty]
        new = set(tv.title) - seen
        rows.append({
            "type": ty, "training pages": len(seen), "test pages": tv.title.nunique(), "new pages": len(new),
            "share of test pages that are new": len(new) / max(tv.title.nunique(), 1),
            "test page views": len(tv), "share of test views on new pages": tv.title.isin(new).mean() if len(tv) else 0.0,
            "test users": tv.User_ID.nunique(), "test users viewing a new page": tv.loc[tv.title.isin(new), "User_ID"].nunique(),
        })
    return pd.DataFrame(rows)


def novelty_by_cohort(pages: pd.DataFrame) -> pd.DataFrame:
    """Per cohort and page type: share of page views on pages that no earlier cohort viewed."""
    rows = []
    for t in range(1, len(MONTH_ORDER)):
        earlier, cur = pages[pages.t0 < t], pages[pages.t0 == t]
        for ty in ("comp", "blog"):
            seen = set(earlier.loc[earlier.type == ty, "title"])
            cv = cur[cur.type == ty]
            rows.append({"cohort": f"M{MONTH_ORDER[t]}" + (" (test)" if t == TEST_T else ""), "type": ty,
                         "pages": cv.title.nunique(), "new pages": len(set(cv.title) - seen),
                         "share of views on new pages": (~cv.title.isin(seen)).mean()})
    return pd.DataFrame(rows)


SUPPORT_BINS = [-1, 0, 9, 49, float("inf")]
SUPPORT_LABELS = ["0 – never seen in training", "1–9 users", "10–49 users", "50+ users"]
SUPPORT_COLORS = [C2, "#bcd5f5", "#6ea4e8", "#1d5fb0"]


def training_support(pages: pd.DataFrame) -> pd.DataFrame:
    """One row per test page view: number of training users behind its per-page / by-type column."""
    train, test = pages[pages.t0 < TEST_T], pages[pages.t0 == TEST_T]
    test = test[test.type.isin(["comp", "blog", "job"])]
    per_page = test.title.map(train.groupby("title").User_ID.nunique()).fillna(0)
    by_type = test.type.map(train.groupby("type").User_ID.nunique()).fillna(0)
    rows = [pd.DataFrame({"column": test.type.map(lambda t: f"{t}_ID_xxx  (per page)"), "support": per_page}),
            pd.DataFrame({"column": "comp / blog / job_page  (by type)", "support": by_type})]
    out = pd.concat(rows, ignore_index=True)
    out["training users behind the column"] = pd.cut(out.support, SUPPORT_BINS, labels=SUPPORT_LABELS)
    return out


def plot_support(support: pd.DataFrame) -> None:
    """100 % stacked bars: how much training data stands behind the column each test page view lands in."""
    order = ["comp_ID_xxx  (per page)", "blog_ID_xxx  (per page)", "job_ID_xxx  (per page)",
             "comp / blog / job_page  (by type)"]
    support = support.assign(column=pd.Categorical(support.column, order))
    counts = support.groupby("column", observed=True).size()

    fig, ax = plt.subplots(figsize=(10, 4.6))
    sns.histplot(data=support, y="column", hue="training users behind the column", multiple="fill",
                 discrete=True, shrink=0.7, hue_order=SUPPORT_LABELS, palette=SUPPORT_COLORS,
                 edgecolor=SURFACE, linewidth=2, alpha=1, ax=ax)
    for bar in ax.patches:
        w = bar.get_width()
        if w >= 0.04:
            light = bar.get_facecolor()[:3] in [matplotlib.colors.to_rgb(c) for c in SUPPORT_COLORS[1:3]]
            ax.text(bar.get_x() + w / 2, bar.get_y() + bar.get_height() / 2, f"{w:.0%}", ha="center",
                    va="center", fontsize=9, color=INK if light else "#ffffff")
    ax.set_yticks(range(len(order)), [f"{c}\n{counts[c]:,} test views" for c in order])
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set(xlabel="share of the test cohort's (M4) page views", ylabel="")
    sns.move_legend(ax, "lower center", bbox_to_anchor=(0.5, 1.0), ncol=4, title="", frameon=False)
    ax.set_title("How many training users (M11–M3) stand behind the column a test page view lands in?",
                 loc="left", fontsize=11, pad=34)
    sns.despine(left=True, bottom=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "page_support.png", dpi=150)


def main() -> None:
    pages = signup_month_page_views()
    test = test_vs_training(pages)
    cohorts = novelty_by_cohort(pages)
    test.to_csv(OUTPUT_DIR / "page_novelty_test.csv", index=False)
    cohorts.to_csv(OUTPUT_DIR / "page_novelty_by_cohort.csv", index=False)

    sns.set_theme(style="whitegrid", rc={"axes.facecolor": SURFACE, "figure.facecolor": SURFACE,
                                         "grid.color": GRID, "text.color": INK, "axes.labelcolor": INK_2,
                                         "xtick.color": INK, "ytick.color": INK_2})
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 9))

    shown = test[test.type != "badge"]
    long = shown.melt(id_vars="type", value_vars=["share of test pages that are new", "share of test views on new pages"],
                      var_name="measure", value_name="share")
    sns.barplot(data=long, x="type", y="share", hue="measure", palette=[C1, C2], ax=ax1)
    for c in ax1.containers:
        ax1.bar_label(c, labels=[f"{v:.0%}" for v in c.datavalues], padding=3, fontsize=9)
    ax1.set_xticks(range(len(shown)),
                   [f"{r.type}\n{r['new pages']} new of {r['test pages']} pages" for _, r in shown.iterrows()])
    ax1.set(ylim=(0, 0.75), xlabel="", ylabel="")
    ax1.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax1.legend(title="", frameon=False, loc="upper left")
    ax1.set_title("Test cohort (M4) vs. training cohorts (M11–M3): pages never seen in training",
                  loc="left", fontsize=11)

    sns.barplot(data=cohorts, x="cohort", y="share of views on new pages", hue="type", palette=[C1, C2], ax=ax2)
    for c in ax2.containers:
        ax2.bar_label(c, labels=[f"{v:.0%}" for v in c.datavalues], padding=3, fontsize=9)
    ax2.set(ylim=(0, 0.85), xlabel="signup cohort", ylabel="")
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax2.legend(title="", frameon=False, loc="upper center", ncol=2)
    ax2.set_title("Every cohort: share of page views on pages that no earlier cohort viewed",
                  loc="left", fontsize=11)
    sns.despine(left=True)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "page_novelty.png", dpi=150)
    support = training_support(pages)
    share = pd.crosstab(support.column, support["training users behind the column"], normalize="index")
    share.to_csv(OUTPUT_DIR / "page_support.csv")
    plot_support(support)
    print(share.round(3).to_string())
    print(test.round(3).to_string(index=False))
    print(cohorts.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
