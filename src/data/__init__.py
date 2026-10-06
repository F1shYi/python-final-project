"""Data layer: read raw CSVs (:mod:`.loading`) and assemble X / Y (:mod:`.dataset`),
split into folds (:mod:`.splits`).

Extension points: label definitions (:mod:`.labels`), feature groups (:mod:`.features`,
``@register``), samplers and feature windows (:class:`.dataset.DatasetSpec`).
"""
from src.data.dataset import XY, DatasetSpec, build_xy, signup_month, submission_user_ids
from src.data.events import MONTH_ORDER, MONTH_TO_T, build_events, build_users
from src.data.features import FEATURE_GROUPS, ActivityCounts, FeatureContext, register
from src.data.labels import NextMonthActive
from src.data.loading import RawData, load_raw
from src.data.splits import Fold, folds_table, kfold_by_user, test_set

__all__ = [
    "RawData", "load_raw", "MONTH_ORDER", "MONTH_TO_T", "build_users", "build_events",
    "NextMonthActive", "FEATURE_GROUPS", "ActivityCounts", "FeatureContext", "register",
    "DatasetSpec", "XY", "build_xy", "signup_month", "submission_user_ids",
    "Fold", "kfold_by_user", "test_set", "folds_table",
]
