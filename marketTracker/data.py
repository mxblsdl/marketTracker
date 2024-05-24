import sqlite3
from datetime import datetime, timedelta
from marketTracker.date_funcs import last_weekday
import requests
import os


def sql_execute(con: sqlite3.Connection, sql: str, params=None) -> tuple:
    """Execute a sql statement and return results

    Args:
        con (sqlite3.Connection): connection object
        sql (str): sql statement
        params (_type_, optional): params to pass into execute statement.
        These are used to fill dynamic values in the sql statement.
        Defaults to None.

    Returns:
        tuple: results returned in tuple
    """
    cur = con.cursor()

    if params is not None:
        cur.execute(sql, params)
        return cur.fetchall()

    cur.execute(sql)
    return cur.fetchall()


def sql_executemany(con: sqlite3.Connection, sql: str, data: list[tuple]) -> None:
    """execute many from a connection.

    Args:
        con (sqlite3.Connection): sqlite3 connection
        sql (str): sql statement. Intented for INSERT statements
        data (list[tuple]): data to insert
    """
    cur = con.cursor()
    cur.executemany(
        sql,
        data,
    )
    con.commit()


def init_database_table(con: sqlite3.Connection) -> None:
    """Initialize data table. Drops all values and recreates table

    Args:
        con (sqlite3.Connection): connection to database
        table (str): Name of table
    """
    sql = "DROP TABLE IF EXISTS funds"
    sql_execute(con, sql)

    sql = """
        CREATE TABLE IF NOT EXISTS funds(
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
    """Retrieve time series data of stocks

    Args:
        ticker (str): Ticker symbol for stock
        func (str, optional): What type of data to retrieve.
        Consult API documenation for further options.
        https://www.alphavantage.co/documentation/#dailyadj
        Defaults to "TIME_SERIES_DAILY".
        output (str, optional): Format for the output data. Compact returns the last 100 data points
        While full returns all historical data. Defaults to "compact".
        api_key (str, optional): API Key for alphavantage API. Defaults to os.getenv("APIKEY").

    Returns:
        list: symbol, date, open, close values
    """
    url = f"https://www.alphavantage.co/query?function={func}&outputsize={output}&symbol={ticker}&apikey={api_key}"
    r = requests.get(url)
    if r.status_code != 200:
        print("Error with API call")
        print(r.reason)
        return

    data = r.json()

    output = [
        [data["Meta Data"]["2. Symbol"]]
        + [k.replace("-", "")]
        + [v["1. open"]]
        + [v["4. close"]]
        for k, v in data["Time Series (Daily)"].items()
    ]
    return output


def max_date(con: sqlite3.Connection) -> datetime.date:
    """Get the most recent date of data from the funds table

    Args:
        con (sqlite3.Connection): Connection to funds database

    Returns:
        datetime.date: date object of the most recent data in database
    """
    cur = con.cursor()
    cur.execute("SELECT MAX(date) FROM funds")
    res = cur.fetchone()
    if res[0] is None:
        return

    return datetime.strptime(res[0], "%Y%m%d").date()


def update_database(
    con: sqlite3.Connection, tickers: list[str], today: datetime.date
) -> None:
    """Update the data in the database. Updates based on the last fully closed day of trading.

    Args:
        con (sqlite3.Connection): Connection to funds table
        tickers (list[str]): list of string symbols for tickers to retrieve data for
        today (datetime.date): The current date
    """
    last_data = last_weekday(today)
    last_data_db = max_date(con)
    if last_data_db == today:
        last_data_db = last_data_db - timedelta(days=1)

    if last_data == last_data_db:
        print("Data is current. No processing will occur")
        return

    print("Initializing database with current data")
    # TODO write to a temp table then migrate
    init_database_table(con)

    for tick in tickers:
        res = get_time_series_daily(
            ticker=tick, output="full", api_key=os.getenv("APIKEY")
        )
        sql = "INSERT INTO funds VALUES(?, ?, ?, ?)"
        sql_executemany(con, sql, res)
