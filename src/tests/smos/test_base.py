from datetime import datetime, timedelta

import pandas as pd
import pytest
from pydantic import ValidationError

from tasi.smos.base import SMOS, TimeSeriesSMOS


class TestSMOS:

    def test_scalar_value(self):
        assert SMOS(value=1.5).value == 1.5


class TestTimeSeriesSMOS:

    def _timestamps(self, n=3):
        t0 = datetime(2024, 1, 1)
        return [t0 + timedelta(seconds=i) for i in range(n)]

    def test_construction(self):
        ts = self._timestamps(3)
        metric = TimeSeriesSMOS(timestamps=ts, values=[1.0, 2.0, 3.0])

        assert len(metric) == 3
        assert metric.timestamps == ts
        assert metric.values == [1.0, 2.0, 3.0]

    def test_mismatched_lengths_raise(self):
        with pytest.raises(ValidationError):
            TimeSeriesSMOS(timestamps=self._timestamps(3), values=[1.0, 2.0])

    def test_series_property(self):
        ts = self._timestamps(3)
        metric = TimeSeriesSMOS(timestamps=ts, values=[1.0, 2.0, 3.0])

        series = metric.series

        assert isinstance(series, pd.Series)
        assert list(series.values) == [1.0, 2.0, 3.0]
        assert list(series.index) == ts
        assert series.name == "timeseriessmos"
