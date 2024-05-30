import yfinance as yf
import sqlite3



def get_mutual_fund_data(ticker: str, time_period: str = "10y"):
    data = yf.Ticker(ticker)

    history = data.history(period=time_period)

    # Transform data
    history = history.reset_index()
    history["Date"] = history.Date.dt.strftime("%Y%m%d")
    history = history[["Date", "Open", "Close"]]
    history["ticker"] = ticker

    history.columns = [c.lower() for c in history.columns]

    return history


def add_mutual_fund_data(con: sqlite3.Connection, tickers: list[str]) -> None:
    for t in tickers:
        d = get_mutual_fund_data(t, time_period="10y")
        d.to_sql(con=con, name="funds", if_exists="append", index=False)
