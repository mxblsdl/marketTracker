from datetime import datetime
from marketTracker.date_funcs import subtract_day
import sqlite3


today = datetime.today().date()

def last_weekday(date: datetime.date) -> datetime.date:
    while date.weekday() >= 5:
        date = subtract_day(date)
    return date


def max_date(con) -> datetime.date:
    cur = con.cursor()
    cur.execute("SELECT MAX(date) FROM funds")
    res = cur.fetchone()
    return datetime.strptime(res[0], "%Y%m%d").date()


con = sqlite3.connect("funds.db")
print(max_date(con) == last_weekday(today))
