"""Evaluation: metrics (:mod:`.metrics`) and cross-validation (:mod:`.cv`)."""
from src.eval.cv import cross_validate, summarize
from src.eval.metrics import f1

__all__ = ["f1", "cross_validate", "summarize"]
