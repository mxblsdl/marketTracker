from shiny import App, Inputs, Outputs, Session, reactive, render, ui, req
import plotnine as pn
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta

from marketTracker.view import (
    get_tickers,
    calc_percent_change,
    get_data_for_date_range,
    date_range,
)
from marketTracker.data import update_database

load_dotenv()

tickers = ["VWO", "VEA", "SCHB", "ESGV", "VTI", "BNDX", "BND"]
con = sqlite3.connect("funds.db")
today = datetime.today().date()

# Update database on load if data is out of date
update_database(con, tickers, today)


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_checkbox_group(
                id="ticks", label="Choose Tickers", choices=get_tickers(con)
        ),
        ui.input_radio_buttons(
            id="timespan",
            label="Choose Timeframe",
            choices={
                1: "1 month",
                2: "2 months",
                3: "3 months",
                6: "6 months",
                12: "1 year",
                24: "2 years",
            },
            selected=3,
        ),
    ),
    ui.output_text("info", container=ui.h3),
    ui.row(
        ui.column(4, ui.output_ui("tickers", fillable=False, fill=True)),
        ui.column(8, ui.output_plot("plots", height="90vh")),
    ),
    window_title="Market Tracker",
    title=ui.output_text("title"),
)


def server(input: Inputs, output: Outputs, session: Session):

    @reactive.calc
    def ticker_data():
        today, past = dates()
        return get_data_for_date_range(con, input.ticks(), today, past)

    @reactive.calc
    @reactive.event(input.timespan, input.ticks)
    def dates():
        return date_range(con, int(input.timespan()))

    @render.plot
    def plots():
        req(input.ticks())
        interval = {
            1: "1 days",
            2: "2 days",
            3: "3 days",
            6: "6 days",
            12: "12 days",
            24: "24 days",
        }
        breaks = interval[int(input.timespan())]

        return (
            pn.ggplot(ticker_data(), pn.aes(x="date", y="close", color="ticker"))
            + pn.geom_line()
            + pn.stat_smooth(method="glm")
            + pn.facet_wrap("ticker", ncol=1, scales="free_y")
            + pn.theme_minimal()
            + pn.theme(axis_text_x=pn.element_text(rotation=45, hjust=1))
            + pn.scale_x_datetime(name="Date", date_breaks=breaks)
        )

    @render.text
    def title():
        today, _ = dates()
        return f"Market Tracker: Data last updated {datetime.strptime(today, "%Y%m%d").date() - timedelta(days=1)}"

    @render.text
    def info():
        return f"Showing data for last {input.timespan()} months"

    @render.ui
    def tickers():
        today, past = dates()
        tags = []
        for t in input.ticks():
            c = calc_percent_change(con, t, today, past)
            tags.append(
                ui.card(c[0], " Percent Change ", str(c[2]))
            )
        return ui.TagList(tags)


app = App(app_ui, server)
app.on_shutdown(con.close)
