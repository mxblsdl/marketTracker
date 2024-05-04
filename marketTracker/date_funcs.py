import holidays
import datetime
from calendar import monthrange


def get_today() -> str:
    """Get today's day in format YYYYMMDD

    Returns:
        str: Date in format YYYYMMDD
    """
    return datetime.datetime.today().strftime("%Y%m%d")


def months_back(month: int) -> str:
    """Retrieve the date in the past by a given number of months

    Args:
        month (int): number of months to look back

    Returns:
        str: date as string for the current date n months back
    """
    today = datetime.datetime.today().date()
    past_month = int(today.month) - int(month)

    if past_month > 0:
        day = get_last_day_of_month(today.day, past_month, today.year)
        return today.replace(month=past_month, year=today.year, day=day).strftime(
            "%Y%m%d"
        )

    past_year = 0
    while past_month <= 0:
        past_month += 12
        past_year += 1

    day = get_last_day_of_month(today.day, past_month, past_year)
    return today.replace(
        month=past_month, year=today.year - past_year, day=day
    ).strftime("%Y%m%d")


def get_last_day_of_month(day: int, month: int, year: int) -> int:
    """Helper function to deal with uneven number of days in months
    Accounts for leap years

    Args:
        day (int): day to check
        month (int): given month
        year (int): given year

    Returns:
        int: valid day for given month and year
    """

    last_day_of_month = monthrange(year, month)[1]
    if day > last_day_of_month:
        day = last_day_of_month
    return day


def add_day(date: str) -> str:
    """Add a day to given string

    Args:
        date (str): date as string

    Returns:
        str: date as string plus one day
    """
    new_date = datetime.datetime.strptime(date, "%Y%m%d") + datetime.timedelta(days=1)
    return new_date.strftime("%Y%m%d")


def subtract_day(date: str | datetime.date) -> str:
    """Remove a day from the current date

    Args:
        date (str | datetime.date): date as date object or string

    Returns:
        str: string representing date minus one. Format: YYYYMMDD
    """
    if date.__class__ in [datetime.date, datetime.datetime]:
        return date + datetime.timedelta(days=-1)

    new_date = datetime.datetime.strptime(date, "%Y%m%d") + datetime.timedelta(days=-1)
    return new_date.strftime("%Y%m%d")


def last_weekday(d: datetime.date) -> datetime.date:
    """Get the last weekday from a given date minus one.
    A single day is subtracted to ensure a full day of trading has closed.
    Accounts for US holidays

    Args:
        d (datetime.date): date to search

    Returns:
        datetime.date: date of the last non-holiday weekday
    """
    us_holidays = holidays.US()

    d = d - datetime.timedelta(days=1)
    while d in us_holidays:
        d = d - datetime.timedelta(days=1)

    while d.weekday() >= 5:
        d = subtract_day(d)
    return d
