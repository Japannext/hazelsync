'''Tests for time utils'''

from datetime import timedelta

from hazelsync.utils.time import duration_parser

class TestDurationParser:
    def test_days(self):
        assert duration_parser('1d') == timedelta(days=1)

    def test_multiple_days(self):
        assert duration_parser('1d 1d 1d') == timedelta(days=3)

    def test_months(self):
        assert duration_parser('2 months') == timedelta(days=60)

    def test_combined(self):
        assert duration_parser('1y6m3d') == timedelta(days=548)
