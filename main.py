from polygon import RESTClient
from dotenv import load_dotenv
import os
import sqlite3

from marketTracker.data import init_database_tables, update_database

load_dotenv()

# Create connection
con = sqlite3.connect("funds.db")
init_database_tables(con, "funds")

# documentation for api client
# https://github.com/polygon-io/client-python?tab=readme-ov-file
# Note I have 5 api calls per minute
client = RESTClient(api_key=os.getenv("APIKEY"))

# Set tickers, only applicable to ETFS
tickers = ["VWO", "VEA", "SCHB", "ESGV", "VTI", "BNDX", "BND"]

update_database(con, client, tickers)

con.close()
