"""Which activities make the M12 cohort "active next month"?

For users who are active in the month after signup (y = 1), compare how often each activity
appears in that label month for the M12 cohort vs. the other labelled cohorts, and split the
M12 cohort by whether ``badge_OCZE`` is their only label-month activity.

Usage::

    python3 scripts/plot_m12_label.py

Output: ``outputs/m12_label_activity.png`` and ``outputs/m12_label_activity.csv``.
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

from src.data import MONTH_TO_T, build_events, build_users, load_raw  # noqa: E402

OUTPUT_DIR = ROOT / "outputs"
M12 = MONTH_TO_T[12]
LAST_LABELLED_T = MONTH_TO_T[3]
TOP_N = 12

INK, INK_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
C_M12, C_OTHER = "#2a78d6", "#eb6834"  # categorical slots 1 and 2
C_INACTIVE = "#c9c8c2"


def label_month_events() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Events in each labelled user's label month (t0 + 1), with a readable ``activity`` column."""
    raw = load_raw(exclude_titles=())  # the chart is about badge_OCZE itself
    users = build_users(raw)
    ev = build_events(raw).merge(users[["t0"]], left_on="User_ID", right_index=True)
    ev = ev[(ev.t == ev.t0 + 1) & (ev.t0 <= LAST_LABELLED_T)].copy()
    act = ev.title.where(ev.source == "activity", ev.source)
    for prefix, name in (("comp_", "comp_* pages"), ("blog_", "blog_* pages"), ("job_", "job_* pages")):
        act = act.mask(act.str.startswith(prefix), name)
    ev["activity"] = act
    return users, ev


def share_of_active_users(ev: pd.DataFrame) -> pd.DataFrame:
    """Share of next-month-active users who did each activity, M12 vs. the other cohorts."""
    groups = {"M12": ev[ev.t0 == M12], "other months": ev[ev.t0 != M12]}
    return pd.DataFrame({
        name: g.groupby("activity").User_ID.nunique() / g.User_ID.nunique() for name, g in groups.items()
    }).fillna(0).sort_values("M12", ascending=False)


def main() -> None:
    users, ev = label_month_events()
    share = share_of_active_users(ev)
    share.to_csv(OUTPUT_DIR / "m12_label_activity.csv")

    m12_acts = ev[ev.t0 == M12].groupby("User_ID").activity.apply(set)
    n_m12 = int((users.t0 == M12).sum())
    only_badge = int(m12_acts.apply(lambda s: s == {"badge_OCZE"}).sum())
    split = pd.DataFrame({
        "group": ["active: badge_OCZE only", "active: other activity", "inactive"],
        "users": [only_badge, len(m12_acts) - only_badge, n_m12 - len(m12_acts)],
    })

    long = (share.head(TOP_N).rename(columns={"other months": "other cohorts (M11, M1–M3)"})
                 .rename_axis("activity").reset_index()
                 .melt(id_vars="activity", var_name="cohort", value_name="share"))

    sns.set_theme(style="whitegrid", rc={"axes.facecolor": SURFACE, "figure.facecolor": SURFACE,
                                         "grid.color": GRID, "text.color": INK, "axes.labelcolor": INK_2,
                                         "xtick.color": INK_2, "ytick.color": INK})
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8.6), height_ratios=[4.2, 1.2])

    sns.barplot(data=long, y="activity", x="share", hue="cohort", orient="h",
                palette=[C_M12, C_OTHER], ax=ax1)
    ax1.set(xlim=(0, 1.05), xlabel="share of next-month-active users", ylabel="")
    ax1.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax1.bar_label(ax1.containers[0], labels=[f"{v:.0%}" if i == 0 else "" for i, v in
                                             enumerate(ax1.containers[0].datavalues)], padding=3, fontsize=9)
    ax1.bar_label(ax1.containers[1], labels=[f"{v:.0%}" if i == 0 else "" for i, v in
                                             enumerate(ax1.containers[1].datavalues)], padding=3, fontsize=9)
    ax1.legend(title="", loc="lower right", frameon=False)
    ax1.set_title("Share of next-month-active users who did each activity in the label month",
                  loc="left", fontsize=11)

    sns.barplot(data=split, y="group", x="users", hue="group", orient="h", legend=False,
                palette=[C_M12, "#7fb2ec", C_INACTIVE], ax=ax2)
    for bar, n in zip(ax2.patches, split.users):
        ax2.text(bar.get_width() + n_m12 * 0.006, bar.get_y() + bar.get_height() / 2,
                 f"{n:,} ({n / n_m12:.0%})", va="center", fontsize=9, color=INK)
    ax2.set(xlim=(0, n_m12 * 0.62), xlabel="users", ylabel="")
    ax2.set_title(f"M12 cohort ({n_m12:,} users) by label-month activity", loc="left", fontsize=11)
    sns.despine(left=True, bottom=True)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "m12_label_activity.png", dpi=150)
    print(f"M12 users {n_m12}, active {len(m12_acts)}, of which badge_OCZE only {only_badge}; "
          f"rate {len(m12_acts) / n_m12:.3f} → {(len(m12_acts) - only_badge) / n_m12:.3f} without badge-only users")
    print(share.head(TOP_N).round(3).to_string())


if __name__ == "__main__":
    main()
