"""Feature groups: each turns the events of a sample's feature window into columns.

A feature group is any callable ``(ctx: FeatureContext) -> DataFrame`` indexed like
``ctx.samples``. Register new groups with :func:`register` and select them by name in
:class:`src.data.dataset.DatasetSpec` (or pass a configured callable such as
``ActivityCounts(binary=True)`` directly); the window events in the context are already
restricted to the feature window, so a group cannot look ahead by construction.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

import pandas as pd

from src.data.loading import RawData


@dataclass
class FeatureContext:
    """Everything a feature group may use.

    Attributes
    ----------
    raw:
        Raw tables (e.g. for entity attributes such as competitions).
    users:
        ``Users.csv`` indexed by ``User_ID`` plus ``t0``.
    samples:
        ``MultiIndex (User_ID, t)``: one row per sample, ``t`` = anchor month.
    window:
        Event log rows inside each sample's feature window, with the extra column ``anchor_t``.
    """

    raw: RawData
    users: pd.DataFrame
    samples: pd.MultiIndex
    window: pd.DataFrame

    def per_sample(self, frame: pd.DataFrame, fill: float | None = None) -> pd.DataFrame:
        """Align a frame indexed by ``(User_ID, anchor_t)`` to :attr:`samples`."""
        out = frame.rename_axis(["User_ID", "t"]).reindex(self.samples)
        return out if fill is None else out.fillna(fill)


FeatureGroup = Callable[[FeatureContext], pd.DataFrame]
FEATURE_GROUPS: dict[str, FeatureGroup] = {}
"""Registry of feature groups, addressable by name."""


def register(name: str) -> Callable[[FeatureGroup], FeatureGroup]:
    """Decorator adding a feature group to :data:`FEATURE_GROUPS`."""
    def deco(fn: FeatureGroup) -> FeatureGroup:
        FEATURE_GROUPS[name] = fn
        return fn
    return deco


@register("profile")
def profile(ctx: FeatureContext) -> pd.DataFrame:
    """Raw ``Users.csv`` columns: FeatureX, FeatureY, Countries_ID (categorical), signup day / hour."""
    users = ctx.users.reindex(ctx.samples.get_level_values("User_ID"))
    out = pd.DataFrame({
        "FeatureX": users["FeatureX"].astype("category"),
        "FeatureY": users["FeatureY"].astype("category"),
        "Countries_ID": users["Countries_ID"].astype("category"),
        "signup_day": users["Created At Day_of_month"],
        "signup_hour": users["Created At time"].str[:2].astype(int),
    })
    return out.set_axis(ctx.samples)


def column_name(activity: str) -> str:
    """Activity name → column name (``"Updated Profile"`` → ``"act_Updated_Profile"``)."""
    return "act_" + re.sub(r"\W+", "_", activity).strip("_")


PAGE_TYPES: dict[str, str] = {"comp_": "comp_page", "blog_": "blog_page", "job_": "job_page", "badge_": "badge"}
"""Title prefix of a specific page → page-type activity name (used with ``by_type=True``)."""


@dataclass(frozen=True)
class ActivityCounts:
    """One column per activity: how often (or whether) the user did it in the window.

    Activities are the raw click ``Title`` values of ``UserActivity.csv`` plus one activity per
    other behaviour table (``join_comp``, ``discussion``, ``comment``). Users who never did an
    activity get 0.

    Parameters
    ----------
    binary:
        ``False`` → number of times (default); ``True`` → 1 if done at least once, else 0.
    by_type:
        ``True`` → titles of specific pages are counted per page type instead of per page
        (``comp_ID_xxx`` → ``comp_page``, ``blog_ID_xxx`` → ``blog_page``, ``job_ID_xxx`` →
        ``job_page``, ``badge_xxx`` → ``badge``; see :data:`PAGE_TYPES`), so pages that first
        appear after the training months still land in a column the model has learned.
    """

    binary: bool = False
    by_type: bool = False

    def __call__(self, ctx: FeatureContext) -> pd.DataFrame:
        ev = ctx.window
        activity = ev.title.where(ev.source == "activity", ev.source)
        if self.by_type:
            for prefix, name in PAGE_TYPES.items():
                activity = activity.mask(activity.str.startswith(prefix), name)
        counts = (ev.assign(activity=activity)
                    .pivot_table(index=["User_ID", "anchor_t"], columns="activity", values="day", aggfunc="size"))
        counts = ctx.per_sample(counts, fill=0).astype(int)
        if self.binary:
            counts = (counts > 0).astype(int)
        names = counts.columns.map(column_name)
        assert names.is_unique, "two activities map to the same column name"
        return counts.set_axis(names, axis=1)


FEATURE_GROUPS["activity_counts"] = ActivityCounts()
FEATURE_GROUPS["activity_flags"] = ActivityCounts(binary=True)
FEATURE_GROUPS["activity_counts_by_type"] = ActivityCounts(by_type=True)
