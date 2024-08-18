import datetime

ALLOWED_DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M",
    "%Y-%m",
)


def parse_date(date_str):
    if isinstance(date_str, str):
        if len(date_str) == 4:
            date_str += "-01-01"  # %Y, let's add Jan01
        elif len(date_str) == 7:
            date_str += "-01"  # %Y-%M, let's add the day to be able to parse
        date_str = date_str.strip()
        for date_fmt in ALLOWED_DATETIME_FORMATS:
            try:
                return datetime.datetime.strptime(date_str, date_fmt)
            except ValueError:
                pass
        raise ValueError(
            f"Invalid date: '{date_str}', please pass a datetime or a string format"
        )
    return date_str
