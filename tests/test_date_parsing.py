import datetime

from spottools import parse_date


class TestDateParsing:
    def test_month(self):
        d = "1967-08"
        e = datetime.datetime(1967, 8, 1)
        assert parse_date(d) == e
