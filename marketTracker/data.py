import sqlite3
from datetime import datetime
from marketTracker.date_funcs import last_weekday
import requests
import os


def sql_execute(con: sqlite3.Connection, sql: str, params=None) -> None:
    """Initialize data and funds table

    Args:
        name (str): _description_
    """
    cur = con.cursor()

    if params is not None:
        cur.execute(sql, params)
        return cur.fetchall()

    cur.execute(sql)
    return cur.fetchall()


def sql_executemany(con: sqlite3.Connection, sql: str, data: list[tuple]) -> None:
    cur = con.cursor()
    cur.executemany(
        sql,
        data,
    )
    con.commit()


def init_database_tables(con: sqlite3.Connection, table: str) -> None:
    # Initialize the table
    sql = f"DROP TABLE IF EXISTS {table}"
    sql_execute(con, sql)

    sql = f"""
        CREATE TABLE IF NOT EXISTS {table}(
        ticker TEXT not null,
        date TEXT not null,
        open REAL not null,
        close REAL not null
        )
        """
    sql_execute(con, sql)


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

    output = [
        [data["Meta Data"]["2. Symbol"]] + [k] + [v["1. open"]] + [v["4. close"]]
        for k, v in data["Time Series (Daily)"].items()
    ]
    return output


def max_date(con) -> datetime.date:
    cur = con.cursor()
    cur.execute("SELECT MAX(date) FROM funds")
    res = cur.fetchone()
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
    # I should really write to a temp table then migrate
    init_database_tables(con, "funds")

    for tick in tickers:
        res = get_time_series_daily(
            ticker=tick, output="full", api_key=os.getenv("APIKEY")
        )
        sql = "INSERT INTO funds VALUES(?, ?, ?, ?)"
        sql_executemany(con, sql, res)

    con.close()
