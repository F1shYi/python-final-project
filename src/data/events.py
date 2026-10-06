"""Common time axis and a unified event log, the shared input of labels and features.

Month codes are masked (official note: chronological, but code 1 is not necessarily January).
:data:`MONTH_ORDER` is the chronological order of the codes; a user cannot be active before
signing up, which fixes the order to ``11 → 12 → 1 → 2 → 3 → 4 → 5``. Internally every month
is a *time index* ``t = 0 … 6`` so that "next month" is simply ``t + 1``.
"""
from __future__ import annotations

import pandas as pd

from src.data.loading import RawData

MONTH_ORDER: tuple[int, ...] = (11, 12, 1, 2, 3, 4, 5)
"""Masked month codes in chronological order (position = time index ``t``)."""

MONTH_TO_T: dict[int, int] = {m: t for t, m in enumerate(MONTH_ORDER)}

EVENT_SOURCES: dict[str, tuple[str, str, str | None]] = {
    # source name: (RawData attribute, column prefix of the time fields, column used as title)
    "activity": ("activity", "datetime", "Title"),
    "join_comp": ("participation", "Created At", "Competition ID"),
    "discussion": ("discussions", "Created At", "Competition ID"),
    "comment": ("comments", "Created At", "Disc_ID"),
}
"""User-level behaviour tables stacked into the event log."""


def build_users(raw: RawData) -> pd.DataFrame:
    """``Users.csv`` indexed by ``User_ID`` plus ``t0`` (time index of the signup month)."""
    users = raw.users.set_index("User_ID")
    return users.assign(t0=users["Created At Month"].map(MONTH_TO_T))


def build_events(raw: RawData) -> pd.DataFrame:
    """Stack the behaviour tables of :data:`EVENT_SOURCES` into one long log.

    Columns: ``User_ID, t, day, time, source, title`` where ``title`` is the click ``Title``
    for activity, the competition ID for joins / discussions and the discussion ID for comments.
    """
    parts = []
    for source, (attr, prefix, title) in EVENT_SOURCES.items():
        df = getattr(raw, attr)
        parts.append(pd.DataFrame({
            "User_ID": df["User_ID"].to_numpy(),
            "t": df[f"{prefix} Month"].map(MONTH_TO_T).to_numpy(),
            "day": df[f"{prefix} Day_of_month"].to_numpy(),
            "time": df[f"{prefix} time"].to_numpy(),
            "source": source,
            "title": df[title].to_numpy(),
        }))
    return pd.concat(parts, ignore_index=True)
