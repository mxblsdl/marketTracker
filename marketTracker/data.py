import sqlite3
from datetime import datetime, timedelta
from marketTracker.date_funcs import last_weekday
from marketTracker.mutual import add_mutual_fund_data


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

    add_mutual_fund_data(con, tickers)
