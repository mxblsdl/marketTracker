import datetime


def get_dates() -> tuple[str]:
    today = datetime.datetime.today()
    end = today.strftime("%Y-%m-%d")
    start = today.replace(year=today.year - 2).strftime("%Y-%m-%d")
    return start, end


def get_today():
    return datetime.datetime.today().strftime("%Y%m%d")


def months_back(month: int) -> str:
    today = datetime.datetime.today()
    past_month = int(today.month) - int(month)
    if past_month > 0:
        return today.replace(month=past_month, year=today.year).strftime("%Y%m%d")

    past_year = 0
    while past_month <= 0:
        past_month += 12
        past_year += 1
    return today.replace(month=past_month, year=today.year - past_year).strftime(
        "%Y%m%d"
    )


def add_day(date: str) -> str:
    new_date = datetime.datetime.strptime(date, "%Y%m%d") + datetime.timedelta(days=1)
    return new_date.strftime("%Y%m%d")


def subtract_day(date: str) -> str:
    if date.__class__ in [datetime.date, datetime.datetime]:
        return date + datetime.timedelta(days=-1)

    new_date = datetime.datetime.strptime(date, "%Y%m%d") + datetime.timedelta(days=-1)
    return new_date.strftime("%Y%m%d")


def last_weekday(date: datetime.date) -> datetime.date:
    # This doesnt take into account holidays...
    while date.weekday() >= 5:
        date = subtract_day(date)
    return date