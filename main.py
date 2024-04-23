from dotenv import load_dotenv
import os
import sqlite3
import requests
from datetime import datetime
from marketTracker.date_funcs import subtract_day
from marketTracker.data import init_database_tables, sql_executemany

"""
Used to emulate the app loading
"""

load_dotenv()

tickers = ["VWO", "VEA", "SCHB", "ESGV", "VTI", "BNDX", "BND"]
con = sqlite3.connect("funds.db")
today = datetime.today().date()


def get_time_series_daily(
    ticker: str,
    func: str = "TIME_SERIES_DAILY",
    output: str = "compact",
    api_key: str = os.getenv("APIKEY"),
) -> list:
    url = f"https://www.alphavantage.co/query?function={func}&outputsize={output}&symbol={ticker}&apikey={api_key}"
    r = requests.get(url)
    if r.status_code != 200:
        print("Error with API call")
        print(r.reason)
        return
    
    data = r.json()

    if "Information" in data.keys():
        print("Rate limit reached. Try again tomorrow")
        exit(1)

    output = [
        [data["Meta Data"]["2. Symbol"]] + [k] + [v["1. open"]] + [v["4. close"]]
        for k, v in data["Time Series (Daily)"].items()
    ]
    return output


def last_weekday(date: datetime.date) -> datetime.date:
    # This doesnt take into account holidays...
    while date.weekday() >= 5:
        date = subtract_day(date)
    return date


def max_date(con) -> datetime.date:
    cur = con.cursor()
    cur.execute("SELECT MAX(date) FROM funds")
    res = cur.fetchone()
    if res[0] is None:
        return

    return datetime.strptime(res[0], "%Y-%m-%d").date()


def update_database(
    con: sqlite3.Connection, tickers: list[str], today: datetime.date
) -> None:
    # Check if data is up to date
    last_data = last_weekday(today)
    last_data_db = max_date(con)
    if last_data == last_data_db:
        print("Data is current. No processing will occur")
        return

    print("Initializing database with current data")
    init_database_tables(con, "funds")

    for tick in tickers:
        res = get_time_series_daily(
            ticker=tick, output="full", api_key=os.getenv("APIKEY")
        )
        sql = "INSERT INTO funds VALUES(?, ?, ?, ?)"
        sql_executemany(con, sql, res)

    con.close()


# init_database_tables(con, "funds")
update_database(con, tickers, today)
