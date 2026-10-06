"""Assemble X and Y from the raw tables.

A dataset is described by a :class:`DatasetSpec` with four independent choices – the design
space of the project:

* ``sampler``        which (user, anchor month) pairs are samples – default: each user's signup month
* ``label``          the target for an anchor month ``t`` – default: any event in month ``t + 1``
* ``feature_groups`` registered feature-group names (:data:`src.data.features.FEATURE_GROUPS`) or
                     configured callables – default: raw profile + one count column per activity
* ``window``         feature window relative to the anchor, ``(start, end)`` in months – default ``(0, 0)``

Typical use::

    from src.data import load_raw, build_xy, DatasetSpec, ActivityCounts
    xy = build_xy(load_raw(), DatasetSpec(feature_groups=("profile", ActivityCounts(binary=True))))
    X_train, y_train = xy.X[xy.labelled], xy.y[xy.labelled]
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from src.data.events import build_events, build_users
from src.data.features import FEATURE_GROUPS, FeatureContext, FeatureGroup
from src.data.labels import LabelFn, NextMonthActive
from src.data.loading import RawData

Sampler = Callable[[pd.DataFrame, pd.DataFrame], pd.MultiIndex]


def signup_month(users: pd.DataFrame, events: pd.DataFrame) -> pd.MultiIndex:
    """One sample per user, anchored at the signup month ``t0``."""
    return pd.MultiIndex.from_arrays([users.index, users.t0], names=["User_ID", "t"])


@dataclass(frozen=True)
class DatasetSpec:
    """How to build X and Y (see the module docstring)."""

    sampler: Sampler = signup_month
    label: LabelFn = field(default_factory=NextMonthActive)
    feature_groups: tuple[str | FeatureGroup, ...] = ("profile", "activity_counts")
    window: tuple[int, int] = (0, 0)


@dataclass
class XY:
    """Model inputs and target, indexed by ``(User_ID, t)``.

    ``y`` is NaN where the next month is not observable (the hidden test cohort and the last
    month of the log); :attr:`labelled` selects the training rows.
    """

    X: pd.DataFrame
    y: pd.Series
    spec: DatasetSpec

    @property
    def t(self) -> pd.Series:
        """Anchor month (time index) of every row, e.g. for time-based CV."""
        return pd.Series(self.X.index.get_level_values("t"), index=self.X.index, name="t")

    @property
    def labelled(self) -> pd.Series:
        """Rows with a known target."""
        return self.y.notna()

    @property
    def categorical(self) -> list[str]:
        """Names of the categorical columns of :attr:`X`."""
        return [c for c in self.X.columns if isinstance(self.X[c].dtype, pd.CategoricalDtype)]


def feature_window(samples: pd.MultiIndex, events: pd.DataFrame, window: tuple[int, int]) -> pd.DataFrame:
    """Events with ``anchor_t + start <= t <= anchor_t + end`` for every sample (column ``anchor_t``)."""
    start, end = window
    if end >= 1:
        raise ValueError(f"feature window {window} overlaps the label month (anchor + 1)")
    anchors = samples.to_frame(index=False).rename(columns={"t": "anchor_t"})
    ev = events.merge(anchors, on="User_ID")
    return ev[(ev.t >= ev.anchor_t + start) & (ev.t <= ev.anchor_t + end)]


def build_xy(raw: RawData, spec: DatasetSpec = DatasetSpec()) -> XY:
    """Build X and Y according to ``spec``."""
    unknown = [g for g in spec.feature_groups if isinstance(g, str) and g not in FEATURE_GROUPS]
    if unknown:
        raise KeyError(f"unknown feature groups {unknown}; available: {sorted(FEATURE_GROUPS)}")
    groups = [FEATURE_GROUPS[g] if isinstance(g, str) else g for g in spec.feature_groups]
    users, events = build_users(raw), build_events(raw)
    samples = spec.sampler(users, events)
    ctx = FeatureContext(raw=raw, users=users, samples=samples,
                         window=feature_window(samples, events, spec.window))
    X = pd.concat([g(ctx) for g in groups], axis=1)
    return XY(X=X, y=spec.label(samples, events), spec=spec)


def submission_user_ids(raw: RawData) -> pd.Index:
    """User IDs to predict, parsed from ``SampleSubmission.csv`` (``ID_xxx_Month_5`` → ``ID_xxx``)."""
    ids = raw.sample_submission["User_ID_Next_month_Activity"].str.rsplit("_Month_", n=1).str[0]
    return pd.Index(ids, name="User_ID")
