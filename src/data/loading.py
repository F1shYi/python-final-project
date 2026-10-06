"""Read the raw competition CSVs with pandas, unchanged.

Entry point: :func:`load_raw` → :class:`RawData` (one DataFrame per CSV).
No cleaning or feature logic lives here; see ``docs.md`` for the meaning of every column.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

RAW_FILES: dict[str, str] = {
    "users": "Users.csv",
    "activity": "UserActivity.csv",
    "participation": "CompetitionPartipation.csv",
    "discussions": "Discussion.csv",
    "comments": "Comments.csv",
    "competitions": "Competition.csv",
    "blogs": "Blogs.csv",
    "jobs": "Jobs.csv",
    "sample_submission": "SampleSubmission.csv",
}
"""Attribute name of :class:`RawData` → file name in ``data/``."""

EXCLUDED_TITLES: tuple[str, ...] = ("badge_OCZE",)
"""Click titles dropped from ``UserActivity.csv`` at load time (affects both features and labels).

``badge_OCZE`` was written for ~3,000 users on one day of month 1 and is the only label-month
activity of half of the M12 cohort, inflating its next-month activity rate from ~29 % to 78 %.
"""


@dataclass
class RawData:
    """The raw tables, one attribute per CSV (see :data:`RAW_FILES`)."""

    users: pd.DataFrame
    activity: pd.DataFrame
    participation: pd.DataFrame
    discussions: pd.DataFrame
    comments: pd.DataFrame
    competitions: pd.DataFrame
    blogs: pd.DataFrame
    jobs: pd.DataFrame
    sample_submission: pd.DataFrame

    def shapes(self) -> pd.DataFrame:
        """Rows / columns of every table."""
        return pd.DataFrame({f.name: getattr(self, f.name).shape for f in fields(self)},
                            index=["rows", "columns"]).T


def load_raw(data_dir: Path | str = DATA_DIR,
             exclude_titles: tuple[str, ...] = EXCLUDED_TITLES) -> RawData:
    """Read every file of :data:`RAW_FILES` from ``data_dir``.

    Parameters
    ----------
    exclude_titles:
        Rows of ``UserActivity.csv`` with these ``Title`` values are dropped
        (``()`` keeps the file unchanged).

    Raises
    ------
    FileNotFoundError
        If any expected file is missing.
    """
    data_dir = Path(data_dir)
    missing = [f for f in RAW_FILES.values() if not (data_dir / f).exists()]
    if missing:
        raise FileNotFoundError(f"missing files in {data_dir}: {missing}")
    tables = {name: pd.read_csv(data_dir / fname) for name, fname in RAW_FILES.items()}
    activity = tables["activity"]
    tables["activity"] = activity[~activity.Title.isin(exclude_titles)].reset_index(drop=True)
    return RawData(**tables)
