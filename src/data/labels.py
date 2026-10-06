"""Target definitions: is the user active in the month after the anchor month?

A label is any callable ``(samples, events) -> Series`` aligned to ``samples`` with values
``1.0 / 0.0 / NaN`` (NaN = not observable). Swap or parametrise it through
:class:`src.data.dataset.DatasetSpec` to explore other definitions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from src.data.events import EVENT_SOURCES, MONTH_TO_T

LabelFn = Callable[[pd.MultiIndex, pd.DataFrame], pd.Series]

HIDDEN_FROM_T = MONTH_TO_T[5]
"""Label months from this time index on are not observable: the next-month activity of the
test cohort (signup month 4, predicted for month 5) is hidden, and month 5 is the end of the log."""


@dataclass(frozen=True)
class NextMonthActive:
    """``1`` if the user has at least one event in month ``t + 1``, else ``0``.

    Parameters
    ----------
    sources:
        Event sources that count as activity (keys of :data:`src.data.events.EVENT_SOURCES`).
    exclude_titles:
        Event titles that do not count as activity (e.g. ``("$identify",)``).
    """

    sources: tuple[str, ...] = tuple(EVENT_SOURCES)
    exclude_titles: tuple[str, ...] = ()

    def __call__(self, samples: pd.MultiIndex, events: pd.DataFrame) -> pd.Series:
        ev = events[events.source.isin(self.sources) & ~events.title.isin(self.exclude_titles)]
        active = pd.MultiIndex.from_frame(ev.assign(t=ev.t - 1)[["User_ID", "t"]])
        y = pd.Series(samples.isin(active).astype(float), index=samples, name="y")
        y[samples.get_level_values("t") + 1 >= HIDDEN_FROM_T] = np.nan
        return y
