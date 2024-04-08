import sqlite3
import datetime
import time
import math
from polygon import RESTClient
from data.date_funcs import get_dates

def sql_execute(con: sqlite3.Connection, sql: str) -> None:
    """Initialize data and funds table

    Args:
        name (str): _description_
    """
    cur = con.cursor()
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
        date TEXT not null,
        open REAL not null,
        close REAL not null,
        ticker TEXT not null
        )
        """
    sql_execute(con, sql)


def get_data(
    client, ticker: str, start: str, end: str, timespan: str = "day"
) -> list[tuple]:
    aggs = []
    for a in client.list_aggs(
        ticker=ticker,
        multiplier=1,
        timespan=timespan,
        from_=start,
        to=end,
        limit=50000,
    ):
        aggs.append(a)

    # Take important information
    return [
        (
            datetime.datetime.fromtimestamp(a.timestamp / 1000, datetime.UTC).strftime(
                "%Y%m%d"
            ),
            a.open,
            a.close,
            ticker,
        )
        for a in aggs
    ]


def update_database(
    con: sqlite3.Connection, client: RESTClient, tickers: list[str]
) -> None:
    # Calculate time
    count = 0
    if len(tickers) > 5:
        print(f"Data update will take about {math.floor(len(tickers) / 5)} minutes")

    # Retrieve today and 2 years ago
    start, end = get_dates()

    for tick in tickers:
        # Factor in sleep for API calls
        if len(tickers) > 5:
            count += 1
        if count > 5:
            time.sleep(60)
            count = 0

        aggs = get_data(client, tick, start, end, "day")

        sql = "INSERT INTO funds VALUES(?, ?, ?, ?)"
        sql_executemany(con, sql, aggs)