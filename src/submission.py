"""Write predictions for the competition test users in the ``SampleSubmission.csv`` format."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.base import BaseEstimator

from src.data.dataset import XY
from src.data.loading import RawData
from src.data.splits import test_set


def make_submission(model: BaseEstimator, xy: XY, raw: RawData, path: Path | str) -> pd.DataFrame:
    """Fit ``model`` on all labelled rows, predict the test users and save the CSV.

    Rows keep the order and ID column of ``SampleSubmission.csv``; ``Active`` holds the 0/1
    predictions of ``model.predict``.
    """
    model.fit(xy.X[xy.labelled], xy.y[xy.labelled].astype(int))
    X_test = test_set(xy, raw)
    pred = pd.Series(model.predict(X_test), index=X_test.index.get_level_values("User_ID"))

    sub = raw.sample_submission.copy()
    ids = sub["User_ID_Next_month_Activity"].str.rsplit("_Month_", n=1).str[0]
    sub["Active"] = pred.reindex(ids).to_numpy().astype(int)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sub.to_csv(path, index=False)
    return sub
