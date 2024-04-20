import sys

# sys.path.insert(0, "../marketTracker/")

import sqlite3
from marketTracker.date_funcs import months_back, add_day, get_today, subtract_day
from marketTracker.data import sql_execute
import pandas as pd


def get_tickers(con):
    res = sql_execute(con, "SELECT DISTINCT ticker FROM funds")
    res = [r[0] for r in res]
    res.sort()
    return res


# Start of date interval code
def get_dates(con):
    res = sql_execute(
        con,
        """
    SELECT DISTINCT date FROM funds
    """,
    )

    return [r[0] for r in res]


def date_range(con: sqlite3.Connection, months: int) -> tuple:
    dates = get_dates(con)

    today = get_today()
    while today not in dates:
        today = subtract_day(today)

    past_date = months_back(months)
    while past_date not in dates:
        past_date = add_day(past_date)
    return today, past_date


def calc_percent_change(
    con: sqlite3.Connection, ticker: str, today: str, past: str
) -> pd.DataFrame:

    if ticker not in get_tickers(con):
        print(f"Ticker: {ticker} not in data")
        return

    sql = f"""SELECT 
    ticker, 
    date,
    ROUND(100 * (1 - LAG(close, 1) OVER (PARTITION BY ticker ORDER BY rowid) / close), 3) AS perc_change
    FROM funds
    WHERE ticker = '{ticker}'
    AND date IN ('{past}', '{today}')"""

    res = sql_execute(con, sql)

    return pd.DataFrame(res, columns=["ticker", "date", "perc_change"])


def get_data_range(
    con: sqlite3.Connection, tickers: tuple[str], today: str, past: str
) -> pd.DataFrame:
    if all([t not in get_tickers(con) for t in tickers]):
        print("1 or more tickers not found in data")
        return
    

    params = ",".join(["?"] * len(tickers))
    sql = f"""SELECT
    ticker,
    date, 
    close
    FROM funds
    WHERE ticker in ({params})
    AND date BETWEEN '{past}' AND '{today}'
    """
    res = pd.DataFrame(
        sql_execute(con, sql, tickers), columns=["ticker", "date", "close"]
    )
    res["date"] = pd.to_datetime(res["date"])

    return res


# con = sqlite3.connect("funds.db")
# get_data_range(con, ("VWO", "VEA"), 1)
