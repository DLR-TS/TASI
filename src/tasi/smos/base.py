from datetime import datetime
from typing import List, Self

import pandas as pd
from pydantic import model_validator

from tasi.io import Position
from tasi.io.public.base import BaseModel


class SMOS(BaseModel):

    #: The SMOS value
    value: float


class TimeSeriesSMOS(BaseModel):
    """Base class for time-series-valued Surrogate Measures of Safety (SMoS).

    Unlike :class:`SMOS`, which holds a single scalar value describing an
    entire interaction (e.g. PET), a `TimeSeriesSMOS` holds one value per
    timestep of an interaction (e.g. TTC, DRAC, THW). It follows the same
    `estimate(...)`-classmethod convention as :class:`SMOS` subclasses.
    """

    #: The timestamps at which the metric was estimated, one per value
    timestamps: List[datetime]

    #: The metric's value at each timestamp
    values: List[float]

    @model_validator(mode="after")
    def _check_lengths_match(self) -> Self:
        if len(self.timestamps) != len(self.values):
            raise ValueError(
                "'timestamps' and 'values' must have the same length, got "
                f"{len(self.timestamps)} and {len(self.values)}"
            )
        return self

    def __len__(self) -> int:
        return len(self.values)

    @property
    def series(self) -> pd.Series:
        """The metric as a `pandas.Series` indexed by timestamp

        Returns:
            pd.Series: The time series of the metric
        """
        return pd.Series(
            self.values,
            index=pd.DatetimeIndex(self.timestamps, name="timestamp"),
            name=type(self).__name__.lower(),
        )
