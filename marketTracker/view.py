import sqlite3
from app.data.date_funcs import months_back, add_day, get_today, subtract_day
from app.data.data import sql_execute


def get_tickers(con):
    res = sql_execute(con, "SELECT DISTINCT ticker FROM funds")
    return [r[0] for r in res]


# Start of date interval code
def get_dates(con):
    res = sql_execute(
        con,
        """
    SELECT DISTINCT date FROM funds
    """,
    )

    return [r[0] for r in res]


def calc_percent_change(db: str, ticker: str, months: int):
    con = sqlite3.connect(db)

    if ticker not in get_tickers(con):
        return
    dates = get_dates(con)

    today = get_today()
    while today not in dates:
        today = subtract_day(today)

    past_date = months_back(months)
    while past_date not in dates:
        past_date = add_day(past_date)

    sql = f"""SELECT 
    ticker, 
    date,
    ROUND(100 * (1 - LAG(close, 1) OVER (PARTITION BY ticker ORDER BY rowid) / close), 3) AS perc_change
    FROM funds
    WHERE ticker = '{ticker}'
    AND date IN ('{past_date}', '{today}')"""

    res = sql_execute(con, sql)
    con.close()

    return res


# print(calc_percent_change("funds.db", "VWO", 3))
